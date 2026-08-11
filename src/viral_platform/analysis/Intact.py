from pathlib import Path

import pandas as pd


def load_intact_reference(filepath):
    """
    Load the processed IntAct virus-host interaction database.

    Parameters
    ----------
    filepath : str or Path
        Path to the processed IntAct TSV file.

    Returns
    -------
    pd.DataFrame
        IntAct virus-host interaction table.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            f"IntAct reference file not found: {filepath}"
        )

    return pd.read_csv(
        filepath,
        sep="\t",
        dtype=str,
    )

def find_intact_interactions(
    intact_df,
    host_genes,
):
    """
    Find IntAct virus-host interactions involving the
    supplied host genes.

    Parameters
    ----------
    intact_df : pd.DataFrame
        Processed IntAct virus-host interaction database.

    host_genes : list[str]
        Host gene symbols to search for.

    Returns
    -------
    pd.DataFrame
        Matching IntAct interactions.
    """

    if not host_genes:
        return intact_df.iloc[0:0].copy()

    # Normalize the user's gene list
    genes = {
        str(gene).strip().upper()
        for gene in host_genes
        if gene is not None and str(gene).strip()
    }

    # Normalize IntAct host gene names
    host_gene_normalized = (
        intact_df["host_gene"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    matches = intact_df[
        host_gene_normalized.isin(genes)
    ].copy()

    return matches.reset_index(drop=True)

def get_virus_display_name(row):
    """
    Get the most useful human-readable viral protein name.
    """
    if pd.notna(row["virus_gene"]) and row["virus_gene"]:
        return row["virus_gene"]

    if pd.notna(row["virus_uniprot"]) and row["virus_uniprot"]:
        return row["virus_uniprot"]

    return row["virus_organism"]

def summarize_intact_interactions(interactions):
    """
    Collapse individual IntAct evidence records into unique
    virus-host interaction pairs.
    """

    if interactions.empty:
        return interactions.copy()

    df = interactions.copy()

    # Stable identifier for the viral node
    df["virus_id"] = df["virus_taxid"]

    # Human-readable name for the viral node
    # df["virus_name"] = df.apply(
    #     get_virus_display_name,
    #     axis=1,
    # )


    df["virus_protein_id"] = df["virus_uniprot"]

    df["virus_protein"] = (
        df["virus_gene"]
        .fillna(df["virus_uniprot"])
    )


    summary = (
        df.groupby(
            ["virus_id", "virus_organism", "virus_protein_id", "virus_protein", "host_gene"],
            dropna=False,
        )
        .agg(
            interaction_count=("interaction_id", "count"),
            publication_count=(
                "publication_id",
                "nunique",
            ),
            publications=(
                "publication",
                lambda x: "; ".join(
                    sorted(
                        {
                            str(value)
                            for value in x
                            if pd.notna(value)
                        }
                    )
                ),
            ),
        )
        .reset_index()
    )

    return summary

def get_significant_de_genes(
    de_results_by_celltype,
    padj_threshold=0.05,
):
    """
    Extract significant DE genes from each cell type.

    A gene is considered significant when:
        padj < padj_threshold

    Returns
    -------
    dict
        Maps each gene to the cell types in which it
        was significantly differentially expressed.
    """

    gene_to_celltypes = {}

    for celltype, results in de_results_by_celltype.items():

        if results is None or results.empty:
            continue

        df = results.copy()

        # Ensure adjusted p-values are numeric
        df["padj"] = pd.to_numeric(
            df["padj"],
            errors="coerce",
        )

        # Select significant DEGs
        significant = df[
            df["padj"] < padj_threshold
        ]

        # Record which cell types each gene
        # was significant in
        for gene in significant["gene"].dropna():

            gene = str(gene).strip()

            if not gene:
                continue

            gene_to_celltypes.setdefault(
                gene,
                [],
            ).append(str(celltype))

    return gene_to_celltypes

def get_de_genes_for_celltype(
    de_results_by_celltype,
    celltype,
    padj_threshold=0.05,
):
    """
    Get significant DE genes for one cell type.
    """

    results = de_results_by_celltype.get(celltype)

    if results is None or results.empty:
        return []

    df = results.copy()

    df["padj"] = pd.to_numeric(
        df["padj"],
        errors="coerce",
    )

    significant = df[
        df["padj"] < padj_threshold
    ]

    return (
        significant["gene"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

def run_intact_interpretation(
    intact_df,
    genes,
    gene_to_celltypes=None,
):
    """
    Match a set of host genes against IntAct and
    attach DE cell-type information.
    """

    # Find raw IntAct evidence
    matches = find_intact_interactions(
        intact_df,
        genes,
    )

    if matches.empty:
        return matches, matches

    # Collapse duplicate/evidence records
    summary = summarize_intact_interactions(
        matches
    )

    if gene_to_celltypes is not None:
        # Attach DE cell-type information
        summary["de_cell_types"] = (
            summary["host_gene"]
            .map(gene_to_celltypes)
            .apply(
                lambda x: ", ".join(x)
                if isinstance(x, list)
                else ""
            )
        )

    return matches, summary

def build_intact_cytoscape_elements(summary_df):

    if summary_df.empty:
        return []

    elements = []

    virus_nodes = {}
    host_nodes = set()

    for _, row in summary_df.iterrows():

        virus_id = str(row["virus_protein_id"])
        virus_name = str(row["virus_protein"])

        if virus_id not in virus_nodes:
            virus_nodes[virus_id] = {
                "data": {
                    "id": f"virus_{virus_id}",
                    "label": virus_name,
                    "node_type": "virus",
                    "virus_id": virus_id,
                    "virus_name": row["virus_name"],
                }
            }

        host_gene = str(row["host_gene"])
        host_node_id = f"host_{host_gene}"

        if host_node_id not in host_nodes:
            elements.append({
                "data": {
                    "id": host_node_id,
                    "label": host_gene,
                    "node_type": "host",
                    "host_gene": host_gene,
                }
            })

            host_nodes.add(host_node_id)

    elements.extend(virus_nodes.values())

    for _, row in summary_df.iterrows():

        virus_id = str(row["virus_protein_id"])
        host_gene = str(row["host_gene"])

        elements.append({
            "data": {
                "id": f"edge_{virus_id}_{host_gene}",
                "source": f"virus_{virus_id}",
                "target": f"host_{host_gene}",
                "interaction_count": int(
                    row["interaction_count"]
                ),
                "publication_count": int(
                    row["publication_count"]
                ),
                "publications": row["publications"],
            }
        })

    return elements