import requests

from .reference_database import ReferenceDatabase
from .app_paths import get_datasets_dir


class ScMOVIRDownloader:

    def __init__(self, database: ReferenceDatabase):
        self.database = database

    def download_file(self, project_id: str, file_type: str) -> bool:
        """
        Download a single reference file.

        Returns
        -------
        bool
            True if downloaded successfully.
            False otherwise.
        """

        file_info = self.database.get_file(project_id, file_type)

        if file_info is None:
            print(f"File '{file_type}' not found for project '{project_id}'.")
            return False

        download_url = file_info["download_url"]

        datasets_dir = get_datasets_dir()
        local_path = datasets_dir / file_info["filename"]

        # Already downloaded?
        if file_info["is_downloaded"] and local_path.exists():
            print(f"{local_path.name} already exists.")
            return True

        # Create directory if necessary
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(local_path, "wb") as f:

                for chunk in response.iter_content(chunk_size=8192):

                    if chunk:
                        f.write(chunk)

            file_size = local_path.stat().st_size

            self.database.update_file_download_status(
                project_id=project_id,
                file_type=file_type,
                is_downloaded=True,
            )

            self.database.update_file_size(
                project_id=project_id,
                file_type=file_type,
                file_size=file_size,
            )

            print(f"Downloaded {local_path.name}")

            return True

        except Exception as e:

            print(f"Download failed: {e}")

            return False

    def download_project(self, project_id: str):
        """
        Download every file belonging to a project.
        """

        files = self.database.get_files(project_id)

        for file in files:

            self.download_file(
                project_id,
                file["file_type"],
            )

    def download_all(self):
        """
        Download every reference file in the database.
        """

        projects = self.database.get_projects()

        for project in projects:

            self.download_project(project["project_id"])