from pathlib import Path
import json
import pandas as pd


class DEGsParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        # Optional cleanup
        df.rename(
            columns={
                "names": "gene",
                "logfoldchanges": "logFC",
                "pct_nz_group": "pct_expressed",
                "Top": "top_status",
            },
            inplace=True,
        )

        return df