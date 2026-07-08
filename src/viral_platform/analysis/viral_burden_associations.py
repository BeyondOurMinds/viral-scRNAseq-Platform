import numpy as np
import logging
import pandas as pd
import time
from scipy.stats import spearmanr
from scipy import sparse
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
    logger.info(f"Filtering genes expressed in fewer than {min_cells} cells. Total genes before filtering: {adata_host.n_vars}")

    keep = expressed_cells >= min_cells
    logger.info(f"Total genes after filtering: {keep.sum()}")
    adata_filtered = adata_host[:, keep]

    # initialize results
    results = []
    total_genes = adata_filtered.n_vars
    zero_variance_skipped = 0
    nan_corr_skipped = 0

    # Use CSC format for fast per-gene column slicing in sparse matrices.
    X = adata_filtered.X
    if sparse.issparse(X):
        X = X.tocsc()

    start_time = time.perf_counter()
    logger.info(f"Starting correlation loop across {total_genes} genes.")

    for i, gene in enumerate(adata_filtered.var_names):
        expression = X[:, i]

        if hasattr(expression, "toarray"):  # Check if it's a sparse matrix
            expression = expression.toarray().ravel()
        else:
            expression = np.asarray(expression).ravel()
        
        if np.std(expression) == 0:
            zero_variance_skipped += 1
            continue

        corr, pval = spearmanr(
            viral_burden,
            expression
        )

        if np.isnan(corr) or np.isnan(pval):
            nan_corr_skipped += 1
            continue

        results.append({
            "gene": gene,
            "spearman_corr": corr,
            "p_value": pval
        })

        if (i + 1) % 500 == 0 or (i + 1) == total_genes:
            elapsed = time.perf_counter() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (total_genes - (i + 1)) / rate if rate > 0 else float("inf")
            logger.info(
                "Processed %d/%d genes (%.1f%%). Elapsed: %.1fs. ETA: %.1fs.",
                i + 1,
                total_genes,
                ((i + 1) / total_genes) * 100 if total_genes else 100.0,
                elapsed,
                remaining if np.isfinite(remaining) else -1,
            )
    logger.info(
        "Spearman correlation analysis completed. Total genes analyzed: %d; zero variance skipped: %d; NaN skipped: %d.",
        len(results),
        zero_variance_skipped,
        nan_corr_skipped,
    )

    results = pd.DataFrame(results)
    logger.info(f"Results DataFrame created with shape: {results.shape}")

    if results.empty:
        logger.warning("No valid host genes remained after filtering/correlation steps.")
        results = pd.DataFrame(columns=["gene", "spearman_corr", "p_value", "adj_p_value"])
        adata.uns["viral_burden_associations"] = results
        set_working_dataset(adata)
        return results

    results = results.sort_values(
        "spearman_corr", ascending=False
    )

    results["adj_p_value"] = multipletests(
        results["p_value"], method="fdr_bh"
    )[1]
    logger.info("FDR adjustment completed using Benjamini-Hochberg method.")

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

    required_cols = {"gene", "spearman_corr", "adj_p_value"}
    missing_cols = required_cols - set(results.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns in results: {sorted(missing_cols)}")

    significant = results[
        results["adj_p_value"] < fdr_threshold
    ].copy()

    positive = significant[
        significant["spearman_corr"] > 0
    ].sort_values("spearman_corr", ascending=False)

    negative = significant[
        significant["spearman_corr"] < 0
    ].sort_values("spearman_corr", ascending=True)

    strong_positive = positive[
        positive["spearman_corr"] >= corr_threshold
    ]

    strong_negative = negative[
        negative["spearman_corr"] <= -corr_threshold
    ]

    logger.info(
        "Significant genes (FDR < %.3f): %d total, %d positive, %d negative.",
        fdr_threshold,
        len(significant),
        len(positive),
        len(negative),
    )
    logger.info(
        "Strong subset (|corr| >= %.3f): %d positive, %d negative.",
        corr_threshold,
        len(strong_positive),
        len(strong_negative),
    )

    if not significant.empty:
        significant["direction"] = np.where(
            significant["spearman_corr"] >= 0,
            "positive",
            "negative",
        )
        significant["passes_corr_threshold"] = (
            np.abs(significant["spearman_corr"]) >= corr_threshold
        )
        significant = significant.sort_values(
            ["adj_p_value", "spearman_corr"],
            ascending=[True, False],
        )

    adata.uns["viral_significant_associations"] = significant
    adata.uns["viral_positive_associations"] = positive
    adata.uns["viral_negative_associations"] = negative
    adata.uns["viral_strong_positive_associations"] = strong_positive
    adata.uns["viral_strong_negative_associations"] = strong_negative

    summary = {
        "genes_tested": len(results),
        "significant_total": len(significant),
        "positive_associations": len(positive),
        "negative_associations": len(negative),
        "strong_positive_associations": len(strong_positive),
        "strong_negative_associations": len(strong_negative),
        "strongest_positive": positive.iloc[0]["gene"] if len(positive) else None,
        "strongest_negative": negative.iloc[0]["gene"] if len(negative) else None,
    }
    logger.info(f"Viral burden association summary: {summary}")

    adata.uns["viral_burden_association_summary"] = summary

    set_working_dataset(adata)

    return significant