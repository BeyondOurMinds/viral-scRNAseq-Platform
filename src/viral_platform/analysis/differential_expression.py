from viral_platform.analysis.pseudobulk import create_pseudobulk, find_biological_replicates
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
import pandas as pd
from scipy.sparse import issparse
import logging

logger = logging.getLogger(__name__)


MIN_PSBULK_CELLS = 10
MIN_PSBULK_COUNTS = 1000
MIN_GENE_COUNT = 10
MIN_SAMPLES_PER_GENE = 2


def run_differential_expression(
    adata,
    grouping,
    group1,
    group2,
    celltype="All Cells",
    min_psbulk_cells=MIN_PSBULK_CELLS,
    min_psbulk_counts=MIN_PSBULK_COUNTS,
    min_gene_count=MIN_GENE_COUNT,
    min_samples_per_gene=MIN_SAMPLES_PER_GENE,
):
    """
    Run differential expression analysis on the given AnnData object based on the specified grouping variable.
    This function checks for biological replicates and creates a pseudobulk dataset before performing DE analysis.

    Parameters:
    - adata: AnnData object containing the dataset.
    - grouping: The column name in adata.obs to group cells for DE analysis.
    - group1: The first group for comparison.
    - group2: The second group for comparison.
    - celltype: The cell type to filter for DE analysis. Default is "All Cells".
    - min_psbulk_cells: Minimum cells per pseudobulk sample kept for DE.
    - min_psbulk_counts: Minimum counts per pseudobulk sample kept for DE.
    - min_gene_count: Minimum count per gene in a sample to be considered expressed.
    - min_samples_per_gene: Minimum number of samples where gene passes min_gene_count.
    Returns:
    - A message indicating the result of the DE analysis or any issues encountered.
    """
    if not find_biological_replicates(adata, grouping):
        return "Insufficient biological replicates for differential expression analysis.", ""
    adata = create_pseudobulk(adata, grouping=grouping)
    if adata is None:
        return "Failed to create pseudobulk dataset for differential expression analysis.", ""

    # Remove tiny pseudobulk profiles that are mostly zeros and can stall DE fitting.
    if "psbulk_cells" in adata.obs.columns and "psbulk_counts" in adata.obs.columns:
        keep_mask = (
            (adata.obs["psbulk_cells"] >= min_psbulk_cells)
            & (adata.obs["psbulk_counts"] >= min_psbulk_counts)
        )
        removed = int((~keep_mask).sum())
        if removed > 0:
            adata = adata[keep_mask].copy()
            logger.info(
                "Filtered %s low-information pseudobulks (<%s cells or <%s counts). Remaining samples: %s",
                removed,
                min_psbulk_cells,
                min_psbulk_counts,
                adata.n_obs,
            )

    if adata.n_obs < 4:
        return "Too few pseudobulk samples after filtering; relax thresholds.", ""

    "DE analysis logic for the selected cell type here"
    counts = prepare_counts(
        adata,
        min_gene_count=min_gene_count,
        min_samples_per_gene=min_samples_per_gene,
    )
    if counts is None or counts.empty or counts.shape[1] == 0:
        logger.warning(
            "Skipping DE for cell type '%s': no informative genes remained after filtering.",
            celltype,
        )
        return "No informative genes remained after filtering.", ""

    metadata = prepare_metadata(adata, grouping)

    present_conditions = set(metadata["condition"].dropna().astype(str).tolist())
    required_conditions = {str(group1), str(group2)}
    if not required_conditions.issubset(present_conditions):
        logger.warning(
            "Skipping DE for cell type '%s': missing group(s) after filtering. Required=%s, present=%s",
            celltype,
            sorted(required_conditions),
            sorted(present_conditions),
        )
        return "Required groups not present after filtering.", ""

    dds = run_deseq2(counts, metadata)
    try:
        results = extract_results(dds, group1, group2)
    except ValueError as exc:
        logger.warning(
            "Skipping DE for cell type '%s' due to invalid contrast (%s vs %s): %s",
            celltype,
            group1,
            group2,
            str(exc),
        )
        return "Invalid contrast after filtering.", ""

    # Here you would implement the actual DE analysis logic
    # For now, we just return a placeholder message
    logger.info("Differential expression analysis completed successfully.")
    return adata, results

def prepare_counts(
    adata,
    min_gene_count=MIN_GENE_COUNT,
    min_samples_per_gene=MIN_SAMPLES_PER_GENE,
):
    if issparse(adata.X):
        counts = pd.DataFrame(
            adata.X.toarray(),
            index=adata.obs_names,
            columns=adata.var_names
        )
    else:
        counts = pd.DataFrame(
            adata.X,
            index=adata.obs_names,
            columns=adata.var_names
        )

    # DESeq2 expects non-negative integer-like counts.
    counts = counts.apply(pd.to_numeric, errors="coerce").fillna(0)
    counts = counts.clip(lower=0).round().astype("int64")

    # Keep genes with a minimal signal across pseudobulk samples.
    informative_gene_mask = (counts >= min_gene_count).sum(axis=0) >= min_samples_per_gene
    counts = counts.loc[:, informative_gene_mask]

    print("Counts DataFrame shape:", counts.shape)
    print("Counts DataFrame dtypes:")
    print(counts.dtypes.value_counts())

    return counts

def prepare_metadata(adata, grouping):
    metadata = adata.obs[[grouping]].copy()
    metadata = metadata.rename(columns={grouping: "condition"})
    metadata["condition"] = metadata["condition"].astype(str)
    print("Metadata columns:", metadata.columns)
    return metadata

def run_deseq2(counts, metadata):
    # Keep identical sample order and shared sample IDs only.
    shared_index = counts.index.intersection(metadata.index)
    counts = counts.loc[shared_index]
    metadata = metadata.loc[shared_index]
    if counts.empty or counts.shape[1] == 0:
        raise ValueError("Counts matrix is empty after aligning with metadata.")
    if metadata.empty:
        raise ValueError("Metadata is empty after aligning with counts.")

    metadata["condition"] = metadata["condition"].astype("category")

    print(type(counts))
    print(counts.dtypes.iloc[:5])
    print(pd.api.types.is_sparse(counts.dtypes.iloc[0]))
    
    dds = DeseqDataSet(
        counts=counts,
        metadata=metadata,
        design="~condition",
    )
    dds.deseq2()
    return dds

def extract_results(dds, group1, group2):
    stat_res = DeseqStats(
        dds,
        contrast=[
            "condition",
            group1,
            group2
        ]
    )
    stat_res.summary()
    results = stat_res.results_df
    results = results.sort_values("padj")
    print("DE results shape:", results.shape)
    print("DE results columns:", results.columns)
    print("DE results head:", results.head())
    return results
    