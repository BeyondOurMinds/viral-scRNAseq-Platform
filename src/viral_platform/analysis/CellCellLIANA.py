import liana as li
from viral_platform.analysis.normalize_adata_x import ensure_log_normalized_x

def run_liana(adata, group_by, method="rank_aggregate", resource="consensus"):
    """
    Run LIANA analysis on the provided AnnData object.

    Parameters
    ----------
    adata : AnnData
        The input AnnData object containing single-cell data.
    group_by : str
        The column in adata.obs to group cells by for the analysis.
    method : str, optional
        The method to use for LIANA analysis. Default is "rank_aggregate".
    resource : str, optional
        The resource to use for ligand-receptor interactions. Default is "consensus".

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the results of the LIANA analysis.
    """
    
    # Initial checks for valid inputs
    if adata is None:
        raise ValueError("No active dataset found for LIANA analysis.")
    if group_by not in adata.obs.columns:
        raise ValueError(f"Group by column '{group_by}' not found in adata.obs.")
    if adata.n_obs == 0 or adata.n_vars == 0:
        raise ValueError("The AnnData object is empty. Please provide a valid dataset.")
    if adata.X is None:
        raise ValueError("The AnnData object does not contain an expression matrix. Please provide a valid dataset.")
    if adata.obs[group_by].nunique() < 2:
        raise ValueError(f"The group_by column '{group_by}' must have at least two unique values for LIANA analysis.")
    
    # Print dataset summary
    print(f"Cells: {adata.n_obs}")
    print(f"Genes: {adata.n_vars}")
    print(f"Cell type column: {group_by}")
    print(f"Cell types: {adata.obs[group_by].unique().tolist()}")

    adata = ensure_log_normalized_x(adata)
    li.mt.rank_aggregate(adata, groupby=group_by, resource_name=resource, use_raw=False)
    liana_results = adata.uns["liana_res"]
    adata.uns["liana_results"] = {
        "Method": method,
        "Resource": resource,
        "Group_by": group_by,
        "Results": liana_results
    }
    return liana_results


# Temp
# from viral_platform.io.loaders import _load_h5ad

# adata = _load_h5ad(r"C:\Users\jtspy\OneDrive\Desktop\Bioinformatics\ViralDatasets\EpsteinBarr\ebv_annotated.h5ad")

# run_liana(adata, group_by="immLow_majority_voting")





