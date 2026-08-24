import liana as li
from viral_platform.analysis.normalize_adata_x import ensure_log_normalized_x


def _prepare_liana_input(adata):
    """Build an AnnData copy for LIANA with log-normalized expression in `.X`."""
    liana_adata = adata.copy()

    if "log_normalized" in adata.layers:
        liana_adata.X = adata.layers["log_normalized"].copy()
        return liana_adata

    return ensure_log_normalized_x(liana_adata, inplace=True)

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

    Stores
    -------
    pd.DataFrame in adata.uns["liana_results"]
        A DataFrame containing the results of the LIANA analysis.
    
    Returns
    -------
    dict
        A summary of the LIANA analysis results, including the number of interactions,
        sender and receiver cell types, and unique ligands and receptors.
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

    liana_adata = _prepare_liana_input(adata)
    li.mt.rank_aggregate(liana_adata, groupby=group_by, resource_name=resource, use_raw=False)
    liana_results = liana_adata.uns["liana_res"]
    

    summary = {
        "n_interactions": len(liana_results),
        "n_sender_celltypes": liana_results["source"].nunique(),
        "n_receiver_celltypes": liana_results["target"].nunique(),
        "n_unique_ligands": liana_results["ligand_complex"].nunique(),
        "n_unique_receptors": liana_results["receptor_complex"].nunique(),
    }
    adata.uns["liana_results"] = {
        "Method": method,
        "Resource": resource,
        "Group_by": group_by,
        "Results": liana_results,
        "Summary": summary
    }
    return adata.uns["liana_results"]["Results"]


def filter_liana_results(
        results,
        source=None,
        target=None,
        ligand=None,
        receptor=None,
        max_magnitude_rank=None,
        max_specificity_rank=None,
):
    """
    Filter LIANA results based on specified criteria.

    Parameters
    ----------
    results : pd.DataFrame
        The DataFrame containing LIANA results.
    source : str, optional
        Filter by sender cell type.
    target : str, optional
        Filter by receiver cell type.
    ligand : str, optional
        Filter by ligand complex.
    receptor : str, optional
        Filter by receptor complex.
    max_magnitude_rank : int, optional
        Filter by maximum magnitude rank (inclusive).
    max_specificity_rank : int, optional
        Filter by maximum specificity rank (inclusive).

    Returns
    -------
    pd.DataFrame
        A filtered DataFrame containing only the rows that match the specified criteria.
    """
    
    filtered_results = results.copy()
    
    if source is not None:
        filtered_results = filtered_results[filtered_results["source"] == source]
    
    if target is not None:
        filtered_results = filtered_results[filtered_results["target"] == target]
    
    if ligand is not None:
        filtered_results = filtered_results[filtered_results["ligand_complex"] == ligand]
    
    if receptor is not None:
        filtered_results = filtered_results[filtered_results["receptor_complex"] == receptor]
    
    if max_magnitude_rank is not None:
        filtered_results = filtered_results[filtered_results["magnitude_rank"] <= max_magnitude_rank]

    if max_specificity_rank is not None:
        filtered_results = filtered_results[filtered_results["specificity_rank"] <= max_specificity_rank]
    
    return filtered_results

def liana_output_table(results):
    """
    Create a Dash DataTable to display LIANA results for only columns: source, target, ligand_complex, receptor_complex, magnitude_rank, specificity_rank.

    Parameters
    ----------
    results : pd.DataFrame
        The DataFrame containing LIANA results.

    Returns
    -------
    dash_table.DataTable
        A Dash DataTable component displaying the LIANA results.
    """
    
    columns_to_display = ["source", "target", "ligand_complex", "receptor_complex", "magnitude_rank", "specificity_rank"]
    results = results[columns_to_display]

    return results

def summarise_celltype_interactions(results):
    summary = (
        results.groupby(["source", "target"])
        .agg(
            interaction_count=("ligand_complex", "count"),
            mean_magnitude=("magnitude_rank", "mean"),
            mean_specificity=("specificity_rank", "mean"),
        )
        .reset_index()
    )
    summary["bubble_size"] = summary["interaction_count"]  # Use interaction count for bubble size
    summary["bubble_color"] = 1 - summary["mean_specificity"]  # Invert specificity for bubble color
    return summary

def summarise_filtered_celltype_interactions(results):
    summary = (
        results.groupby(["source", "target"])
        .agg(
            interaction_count=("ligand_complex", "count"),
            mean_magnitude=("magnitude_rank", "mean"),
            mean_specificity=("specificity_rank", "mean"),
        )
        .reset_index()
    )
    summary["bubble_size"] = 1 - summary["mean_magnitude"]  # Use interaction count for bubble size
    summary["bubble_color"] = 1 - summary["mean_specificity"]  # Invert specificity for bubble color
    return summary



