from pathlib import Path
import json

import pandas as pd


class UMAPParser:
    """Parser for scMOVIR UMAP JSON files."""

    REQUIRED_COLUMNS = [
        "umap_1",
        "umap_2",
        "cell_type"
    ]

    @staticmethod
    def parse(file_path: str | Path) -> pd.DataFrame:
        """
        Parse a scMOVIR UMAP JSON file.

        Parameters
        ----------
        file_path
            Path to the downloaded UMAP JSON file.

        Returns
        -------
        pd.DataFrame
            Indexed by cell ID with columns:

            umap_1
            umap_2
            cell_type
        """

        file_path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rows = []

        for cluster in data:

            cluster_name = cluster["name"]

            for point in cluster["data"]:

                rows.append(
                    {
                        "cell_id": point[2],
                        "umap_1": float(point[0]),
                        "umap_2": float(point[1]),
                        "cell_type": point[3] if len(point) > 3 else cluster_name,
                    }
                )

        df = pd.DataFrame(rows).set_index("cell_id")

        UMAPParser._validate(df)

        return df

    @staticmethod
    def _validate(df: pd.DataFrame) -> None:
        """Validate parsed UMAP data."""

        missing = [
            column
            for column in UMAPParser.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"UMAP file missing required columns: {missing}"
            )

        if df.empty:
            raise ValueError("UMAP file contains no cells.")