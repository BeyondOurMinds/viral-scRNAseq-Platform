from pathlib import Path
import json
import pandas as pd


class CellTypeBoxplotParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        rows = []

        for cell_type, conditions in data.items():
            for condition, samples in conditions.items():
                for sample in samples:
                    rows.append(
                        {
                            "cell_type": cell_type,
                            "condition": condition,
                            "sample_accession": sample["Sample_geo_accession"],
                            "proportion": sample["proportion"],
                        }
                    )

        return pd.DataFrame(rows)
    
class CellTypePieParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        df.rename(
            columns={
                "name": "cell_type",
                "value": "proportion",
            },
            inplace=True,
        )

        return df
    
class CellTypeStackedBarParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        rows = []

        samples = data["Sample"]

        for cell_type, values in zip(data["Celltype"], data["Values"]):
            for sample, proportion in zip(samples, values):
                rows.append(
                    {
                        "sample_accession": sample,
                        "cell_type": cell_type,
                        "proportion": proportion,
                    }
                )

        return pd.DataFrame(rows)
    
class CellTypeTableParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        df.rename(
            columns={
                "Condition": "condition",
                "Sample accession": "sample_accession",
                "Cell type": "cell_type",
                "Proportion": "proportion",
            },
            inplace=True,
        )

        return df