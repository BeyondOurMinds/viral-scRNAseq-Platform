from pathlib import Path

import pandas as pd

from .reference_database import ReferenceDatabase

FILE_TEMPLATES = [

    ("OBS_ANNOTATION",          "{acc}_obs.annot.csv"),
    ("SAMPLE_INFO",             "{acc}_sampleInfo.csv"),
    ("UMAP",                    "{acc}_umap.json"),
    ("DEGS",                    "{acc}_DEGs.json"),
    ("DEGS_TOP",                "{acc}_DEGs_top.json"),
    ("ORA",                     "{acc}_ORA.json"),
    ("ORA_TOP",                 "{acc}_ORA_top.json"),
    ("CELLPHONEDB",             "{acc}_cellphonedb.json"),
    ("CELLPHONEDB_DCC",         "{acc}_cellphonedb_DCC.csv"),
    ("CELLPHONEDB_TOP",         "{acc}_cellphonedb_top.json"),
    ("CELLTYPE_FRAC_BOXPLOT",   "{acc}_celltype_frac_boxplot.json"),
    ("CELLTYPE_FRAC_PIE",       "{acc}_celltype_frac_pie.json"),
    ("CELLTYPE_FRAC_STACKED",   "{acc}_celltype_frac_stackedbar.json"),
    ("CELLTYPE_TABLE",          "{acc}_celltype_table.json"),
    ("GENE_HEATMAP",            "{acc}_gene_heatmap.json"),

]

BASE_URL = "https://pgx.zju.edu.cn/assets/scmovir/scRNA"



class ScMOVIRImporter:
    """Import scMOVIR metadata into the local SQLite database."""

    def __init__(
        self,
        database: ReferenceDatabase,
    ):

        self.database = database

    def import_projects(
        self,
        project_information_path: str | Path,
        project_annotation_path: str | Path,
    ):

        # --------------------------------------------------
        # Read spreadsheets
        # --------------------------------------------------

        info = pd.read_excel(project_information_path)

        annotation = pd.read_excel(project_annotation_path)

        #--------------------------------------------------
        # Check that the project IDs match between the two files
        #--------------------------------------------------

        info_ids = set(info["Project_ID"])
        annotation_ids = set(annotation["Project_ID"])

        if info_ids != annotation_ids:
            raise ValueError(
                "Project IDs do not match between the two metadata files."
            )

        # --------------------------------------------------
        # Merge into one dataframe
        # --------------------------------------------------

        projects = info.merge(
            annotation,
            on="Project_ID",
            how="left",
            suffixes=("_info", "_annotation"),
        )

        print(f"Importing {len(projects)} projects...")
        

        # --------------------------------------------------
        # Insert projects
        # --------------------------------------------------

        for _, row in projects.iterrows():

            self._insert_project(row)

            project_id = row["Project_ID"]
            accession = row["Project_accession"]

            self._insert_files(
                project_id,
                accession
            )

        self.database.connection.commit()

        print("Finished importing projects.")


    def _insert_project(self, row):

        self.database.cursor.execute(

            """
            INSERT OR REPLACE INTO projects (

                project_id,
                accession,
                title,
                virus_family,
                virus_species,
                virus_subtype,
                disease,
                disease_category,
                tissue,
                pmid,
                platform,
                summary,
                design

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                row["Project_ID"],
                row["Project_accession"],
                row["Project_title_info"],
                row["Virus_family"],
                row["Virus_species"],
                row["Virus_subtype"],
                row["Disease"],
                row["Disease_category"],
                row["Tissue"],
                row["Series_pubmed_id"],
                row["Platforms"],
                row["Project_summary"],
                row["Project_overall_design"],

            ),

        )
    
    def _insert_files(self, project_id, accession):

        for file_type, filename_template in FILE_TEMPLATES:

            filename = filename_template.format(acc=accession)

            download_url = (
                f"{BASE_URL}/{accession}/{filename}"
            )

            local_path = (
                f"src/viral_platform/datasets/{accession}/{filename}"
            )

            self.database.cursor.execute(
                """
                INSERT OR REPLACE INTO files
                (
                    project_id,
                    file_type,
                    filename,
                    local_path,
                    download_url,
                    is_downloaded
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    file_type,
                    filename,
                    local_path,
                    download_url,
                    0,
                ),
            )