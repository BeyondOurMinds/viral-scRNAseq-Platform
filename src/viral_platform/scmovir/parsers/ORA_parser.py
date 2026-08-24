from pathlib import Path
import json
import pandas as pd


class ORAParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        # Optional cleanup
        df.rename(
            columns={
                "Gene_set": "gene_set",
                "Term": "term",
                "Overlap": "overlap",
                "P-value": "p_value",
                "Adjusted P-value": "adjusted_p_value",
                "Odds Ratio": "odds_ratio",
                "Combined Score": "combined_score",
                "Genes": "genes",
                "Cell_type": "cell_type",
                "Condition": "condition",
                "Gene_count": "gene_count",
                "Gene_ratio": "gene_ratio",
                "-log10FDR": "neg_log10_fdr",
                "Top": "top_status",
            },
            inplace=True,
        )

        return df