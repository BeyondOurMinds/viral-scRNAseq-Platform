from pathlib import Path

from viral_platform.scmovir.reference_database import ReferenceDatabase

from viral_platform.scmovir.downloader import ScMOVIRDownloader

DATABASE = Path(
    "src/viral_platform/scmovir/scmovir.db"
)

db = ReferenceDatabase(DATABASE)

downloader = ScMOVIRDownloader(db)

# downloader.download_file(
#     project_id="SCDR00004",
#     file_type="OBS_ANNOTATION",
# )

db.remove_downloaded_file(
    project_id="SCDR00004",
    file_type="OBS_ANNOTATION"
)