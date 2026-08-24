from .reference_database import ReferenceDatabase
from .downloader import ScMOVIRDownloader


class ReferenceManager:
    def __init__(self, database: ReferenceDatabase):
        self.database = database
        self.downloader = ScMOVIRDownloader(database)

    def search_projects(self, virus_species: str = None, disease: str = None, tissue: str = None, platform: str = None):
        return self.database.search_projects(
            virus_species=virus_species,
            disease=disease,
            tissue=tissue,
            platform=platform
        )
    
    def update_download_status(self, project_id: str, file_type: str, is_downloaded: bool):
        self.database.update_file_download_status(
            project_id=project_id,
            file_type=file_type,
            is_downloaded=is_downloaded
        )
    
    def update_file_size(self, project_id: str, file_type: str, file_size: int):
        self.database.update_file_size(
            project_id=project_id,
            file_type=file_type,
            file_size=file_size
        )
    
    def get_files(self, project_id: str):
        return self.database.get_files(project_id)
    
    def get_file(self, project_id: str, file_type: str):
        return self.database.get_file(project_id, file_type)
    
    def get_project(self, project_id: str):
        return self.database.get_project(project_id)
    
    def list_projects(self):
        return self.database.list_projects()
    
    def get_project_count(self):
        return self.database.get_project_count()
    
    def download_file(self, project_id: str, file_type: str) -> bool:
        return self.downloader.download_file(project_id, file_type)
    
    def download_project(self, project_id: str):
        self.downloader.download_project(project_id)
    
    def download_all(self):
        self.downloader.download_all()
    
    def remove_downloaded_file(self, project_id: str, file_type: str):
        self.database.remove_downloaded_file(project_id, file_type)

    def remove_downloaded_project(self, project_id: str):
        self.database.remove_downloaded_project_files(project_id)
    
    def get_reference_summary(self, project_id: str):
        return self.database.get_reference_summary(project_id)