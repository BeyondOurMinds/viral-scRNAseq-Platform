import numpy as np
import logging
import pandas as pd
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests

from viral_platform.state.dataset_store import get_working_dataset, set_working_dataset

logger = logging.getLogger(__name__)

def calculate_viral_burden_associations(viral_features, min_cells=10):
    """
    Calculate Spearman correlation between viral burden and viral features.

    Parameters
    ----------
    viral_features : list
        List of viral feature names to correlate with viral burden.
    min_cells : int
        Minimum number of cells expressing a feature to include in the analysis.

    Returns
    -------
    pd.DataFrame
        DataFrame containing Spearman correlation"""
    
    adata = get_working_dataset()
    if adata is None:
        logger.error("No active dataset found for viral burden association analysis.")
        raise ValueError("No active dataset found for viral burden association analysis.")
    if 'viral_burden' not in adata.obs.columns:
        logger.error("Viral burden has not been calculated. Please run viral burden analysis first.")
        raise ValueError("Viral burden has not been calculated. Please run viral burden analysis first.")
    
    viral_burden = adata.obs['viral_burden'].to_numpy()

    # Removing viral genes from the dataset to focus on host genes for correlation analysis
    host_mask = ~adata.var_names.isin(viral_features)
    adata_host = adata[:, host_mask]

    # Remove genes expressed in fewer than min_cells
    expressed_cells = np.asarray(
        (adata_host.X > 0).sum(axis=0)
    ).ravel()

    keep = expressed_cells >= min_cells
    adata_filtered = adata_host[:, keep]

    # initialize results
    results = []

    for i, gene in enumerate(adata_filtered.var_names):
        expression = adata_filtered.X[:, i]

        if hasattr(expression, "toarray"):  # Check if it's a sparse matrix
            expression = expression.toarray().ravel()
        else:
            expression = np.asarray(expression).ravel()
        
        if np.std(expression) == 0:
            logger.warning(f"Gene {gene} has zero variance in expression. Skipping correlation.")
            continue

        corr, pval = spearmanr(
            viral_burden,
            expression
        )

        if np.isnan(corr) or np.isnan(pval):
            logger.warning(f"Spearman correlation returned NaN for gene {gene}. Skipping.")
            continue

        results.append({
            "gene": gene,
            "spearman_corr": corr,
            "p_value": pval
        })

    results = pd.DataFrame(results)

    results = results.sort_values(
        "spearman_corr", ascending=False
    )

    results["adj_p_value"] = multipletests(
        results["p_value"], method="fdr_bh"
    )[1]

    adata.uns["viral_burden_associations"] = results

    set_working_dataset(adata)

    return results

def identify_significant_associations(results, corr_threshold=0.3, fdr_threshold=0.05):
    """
    Identify significant associations based on correlation and FDR thresholds.

    Parameters
    ----------
    results : pd.DataFrame
        DataFrame containing Spearman correlation results.
    corr_threshold : float
        Minimum absolute correlation value to consider an association significant.
    fdr_threshold : float
        Maximum FDR-adjusted p-value to consider an association significant.

    Returns
    -------
    pd.DataFrame
        DataFrame containing significant associations.
    """
    
    adata = get_working_dataset()

    positive = results[
        (results["spearman_corr"] >= corr_threshold) &
        (results["adj_p_value"] < fdr_threshold)
    ]
    negative = results[
        (results["spearman_corr"] <= -corr_threshold) &
        (results["adj_p_value"] < fdr_threshold)
    ]
    
    positive = positive.sort_values("spearman_corr", ascending=False)
    negative = negative.sort_values("spearman_corr", ascending=True)

    adata.uns["viral_positive_associations"] = positive
    adata.uns["viral_negative_associations"] = negative

    summary = {
        "genes_tested": len(results),
        "positive_associations": len(positive),
        "negative_associations": len(negative),
        "strongest_positive": positive.iloc[0]["gene"] if len(positive) else None,
        "strongest_negative": negative.iloc[0]["gene"] if len(negative) else None
    }

    adata.uns["viral_burden_association_summary"] = summary

    set_working_dataset(adata)

    # debug statements
    print("\nTop positive associations")
    print(
        positive[
            ["gene", "spearman_corr", "adj_p_value"]
        ].head(10)
    )

    print("\nTop negative associations")
    print(
        negative[
            ["gene", "spearman_corr", "adj_p_value"]
        ].head(10)
    )

    return summary