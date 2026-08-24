from pathlib import Path

from viral_platform.scmovir.reference_database import ReferenceDatabase
from viral_platform.scmovir.importer import ScMOVIRImporter


DATABASE = Path("src/viral_platform/scmovir/scmovir.db")

if DATABASE.exists():
    DATABASE.unlink()

PROJECT_INFORMATION = Path("src/viral_platform/scmovir/scRNA_project_information.xlsx")

PROJECT_ANNOTATION = Path("src/viral_platform/scmovir/scRNA_project_annotation.xlsx")


db = ReferenceDatabase(DATABASE)

db.create_tables()

importer = ScMOVIRImporter(db)

importer.import_projects(

    PROJECT_INFORMATION,
    PROJECT_ANNOTATION,

)

print(f"Projects imported: {db.get_project_count()}")

print(dict(db.get_project("SCDR00050")))

db.close()

print("Reference database successfully built.")