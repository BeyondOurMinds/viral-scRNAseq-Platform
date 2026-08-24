from pathlib import Path
import sqlite3
from .app_paths import get_datasets_dir


class ReferenceDatabase:
    """SQLite interface for the local scMOVIR reference database."""

    def __init__(self, database_path: str | Path):

        self.database_path = Path(database_path)

        self.connection = sqlite3.connect(self.database_path)

        self.connection.execute("PRAGMA foreign_keys = ON;")

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

    def close(self):

        self.connection.close()
    
    def get_project_count(self):

        result = self.cursor.execute(
            "SELECT COUNT(*) FROM projects"
        ).fetchone()

        return result[0]

    def list_projects(self):

        return self.cursor.execute(
            """
            SELECT
                project_id,
                title,
                virus_species,
                disease,
                tissue
            FROM projects
            """
        ).fetchall()

    def get_project(self, project_id):

        return self.cursor.execute(
            """
            SELECT *
            FROM projects
            WHERE project_id = ?
            """,
            (project_id,)
        ).fetchone()
    
    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (

                project_id TEXT PRIMARY KEY,

                accession TEXT NOT NULL,

                title TEXT,

                virus_family TEXT,
                virus_species TEXT,
                virus_subtype TEXT,

                disease TEXT,
                disease_category TEXT,

                tissue TEXT,

                pmid TEXT,

                platform TEXT,

                summary TEXT,

                design TEXT

            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                project_id TEXT NOT NULL,

                file_type TEXT NOT NULL,

                filename TEXT NOT NULL,

                local_path TEXT,

                download_url TEXT NOT NULL,

                is_downloaded INTEGER NOT NULL DEFAULT 0,

                file_size INTEGER,

                FOREIGN KEY(project_id)
                    REFERENCES projects(project_id),

                UNIQUE(project_id, file_type)

            );
            """
        )

    def get_file(self, project_id, file_type):

        return self.cursor.execute(
            """
            SELECT *
            FROM files
            WHERE project_id = ? AND file_type = ?
            """,
            (project_id, file_type)
        ).fetchone()
    
    def get_files(self, project_id):
        """
        Get all files associated with a specific project.
        """

        return self.cursor.execute(
            """
            SELECT *
            FROM files
            WHERE project_id = ?
            """,
            (project_id,)
        ).fetchall()
    
    def update_file_download_status(self, project_id, file_type, is_downloaded):
        """
        Update the download status for a specific file in the database.
        """

        self.cursor.execute(
            """
            UPDATE files
            SET is_downloaded = ?
            WHERE project_id = ? AND file_type = ?
            """,
            (is_downloaded, project_id, file_type)
        )

        self.connection.commit()
    
    def update_file_size(self, project_id, file_type, file_size):
        """
        Update the file size for a specific file in the database.
        """

        self.cursor.execute(
            """
            UPDATE files
            SET file_size = ?
            WHERE project_id = ? AND file_type = ?
            """,
            (file_size, project_id, file_type)
        )

        self.connection.commit()
    
    def search_projects(self, virus_species: str = None, disease: str = None, tissue: str = None, platform: str = None):
        """
        Search for projects based on virus species, disease, tissue, and platform.
        Returns a list of matching projects.
        """
        query = "SELECT * FROM projects WHERE 1=1"
        params = []

        if virus_species:
            query += " AND virus_species LIKE ?"
            params.append(f"%{virus_species}%")

        if disease:
            query += " AND disease LIKE ?"
            params.append(f"%{disease}%")

        if tissue:
            query += " AND tissue LIKE ?"
            params.append(f"%{tissue}%")

        if platform:
            query += " AND platform LIKE ?"
            params.append(f"%{platform}%")

        return self.database.cursor.execute(query, params).fetchall()
    
    def remove_downloaded_file(self, project_id: str, file_type: str):
        """
        Remove the downloaded file from the local storage and update the database.
        """
        file_record = self.get_file(project_id, file_type)
        if file_record and file_record["is_downloaded"]:
            local_path = get_datasets_dir() / file_record["filename"]
            if local_path.exists():
                local_path.unlink()  # Delete the file
            self.update_file_download_status(project_id, file_type, is_downloaded=False)
            self.update_file_size(project_id, file_type, file_size=None)
    
    def remove_downloaded_project_files(self, project_id: str):
        """
        Remove all downloaded files for a specific project.
        """
        files = self.get_files(project_id)
        for file in files:
            self.remove_downloaded_file(project_id, file["file_type"])

    def get_reference_summary(self, project_id: str):
        """
        Get a summary of the reference data for a specific project.
        """
        project = self.get_project(project_id)
        file_count = self.cursor.execute(
            "SELECT COUNT(*) FROM files WHERE project_id = ?",
            (project_id,)
        ).fetchone()[0]

        return {
            "title": project["title"],
            "virus": project["virus_species"],
            "disease": project["disease"],
            "tissue": project["tissue"],
            "platform": project["platform"],
            "file_count": file_count
        }