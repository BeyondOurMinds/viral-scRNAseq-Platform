from viral_platform.state.dataset_store import get_dataset
from viral_platform.analysis.pseudobulk import create_pseudobulk, find_biological_replicates, subset_cells
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
import pandas as pd
from scipy.sparse import issparse
import logging

logger = logging.getLogger(__name__)


def run_differential_expression(adata, grouping, group1, group2, celltype="All Cells"):
    """
    Run differential expression analysis on the given AnnData object based on the specified grouping variable.
    This function checks for biological replicates and creates a pseudobulk dataset before performing DE analysis.

    Parameters:
    - adata: AnnData object containing the dataset.
    - grouping: The column name in adata.obs to group cells for DE analysis.
    - group1: The first group for comparison.
    - group2: The second group for comparison.
    - celltype: The cell type to filter for DE analysis. Default is "All Cells".
    Returns:
    - A message indicating the result of the DE analysis or any issues encountered.
    """
    if not find_biological_replicates(adata, grouping):
        return "Insufficient biological replicates for differential expression analysis.", ""
    adata = create_pseudobulk(adata)
    if adata is None:
        return "Failed to create pseudobulk dataset for differential expression analysis.", ""
    "DE analysis logic for the selected cell type here"
    counts = prepare_counts(adata)
    metadata = prepare_metadata(adata, grouping)
    dds = run_deseq2(counts, metadata)
    results = extract_results(dds, group1, group2)

    # Here you would implement the actual DE analysis logic
    # For now, we just return a placeholder message
    logger.info("Differential expression analysis completed successfully.")
    return adata, results

def prepare_counts(adata):
    if issparse(adata.X):
        counts = pd.DataFrame.sparse.from_spmatrix(
            adata.X,
            index=adata.obs_names,
            columns=adata.var_names
        )
    else:
        counts = pd.DataFrame(
            adata.X,
            index=adata.obs_names,
            columns=adata.var_names
        )
    print("Counts DataFrame shape:", counts.shape)
    return counts

def prepare_metadata(adata, grouping):
    metadata = adata.obs.copy()
    metadata = metadata.rename(
        columns={
            grouping: "condition"
        }
    )
    print("Metadata columns:", metadata.columns)
    return metadata

def run_deseq2(counts, metadata):
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
    