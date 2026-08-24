from pathlib import Path
import json
import pandas as pd


class GeneHeatmapParser:
    @staticmethod
    def parse(path: str | Path) -> pd.DataFrame:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        clusters = data["cluster_name"]
        genes = data["gene_name"]

        rows = []

        for cluster_idx, gene_idx, expression in data["values"]:
            rows.append(
                {
                    "cluster_order": cluster_idx,
                    "gene_order": gene_idx,
                    "cluster_name": clusters[cluster_idx],
                    "gene_name": genes[gene_idx],
                    "expression": expression,
                }
            )

        return pd.DataFrame(rows)
