from pathlib import Path
import json
import pandas as pd


class CellPhoneDBParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        # Optional cleanup
        df.rename(
            columns={
                "Condition": "condition",
                "Top": "top_status",
            },
            inplace=True,
        )

        return df
    
class CellPhoneDBDCCParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        df = pd.read_csv(path)

        # Optional cleanup
        df.rename(
            columns={
                "FC": "fold_change",
            },
            inplace=True,
        )

        return df