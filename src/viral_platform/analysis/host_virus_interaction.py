from viral_platform.analysis.viral_gene_detection import normalize_gene_name
from scipy.stats import spearmanr
from scipy import sparse
import logging
import pandas as pd
from statsmodels.stats.multitest import multipletests
import numpy as np
import time

logger = logging.getLogger(__name__)

def get_features_for_gene(adata, selected_gene):

    features = []

    for feature in adata.var_names:

        gene = normalize_gene_name(feature)

        if gene == selected_gene:
            features.append(feature)

    return features

def host_virus_interaction(adata, features, selected_gene, selected_gene_features, min_cells=10):
    # grabbing raw counts matrix from adata.layers["counts"]
    matrix = (adata.layers["counts"])

    if not selected_gene:
        logger.warning("Host-virus interaction called without a selected viral gene.")
        return pd.DataFrame(columns=["gene", "correlation", "p_value", "adjusted_p"])

    if not selected_gene_features:
        logger.warning("No dataset features matched selected viral gene '%s'.", selected_gene)
        return pd.DataFrame(columns=["gene", "correlation", "p_value", "adjusted_p"])

    # extracting only viral features
    viral_matrix = matrix[:, adata.var_names.isin(selected_gene_features)].copy()

    # Sum viral counts per cell
    viral_expression = viral_matrix.sum(axis=1)
    if hasattr(viral_expression, "A1"):  # Check if it's a sparse matrix
        viral_expression = viral_expression.A1  # Convert to 1D array
    else:
        viral_expression = np.array(viral_expression).flatten()  # Ensure it's a 1D array
    
    # Log transform
    viral_expression = np.log1p(viral_expression)

    # Spearman correlation is undefined when one input is constant.
    if viral_expression.size == 0 or np.nanstd(viral_expression) == 0:
        results = pd.DataFrame(columns=["gene", "correlation", "p_value", "adjusted_p"])
        if "host_virus_interactions" not in adata.uns:
            adata.uns["host_virus_interactions"] = {}
        adata.uns["host_virus_interactions"][selected_gene] = results
        return results
    
    host_mask = ~adata.var_names.isin(features)

    host_adata = adata[:, host_mask]

    expressed = np.asarray(
        (host_adata.X > 0).sum(axis=0)
    ).ravel()

    keep = expressed >= min_cells

    host_adata = host_adata[:, keep]
    if host_adata.n_vars == 0:
        logger.warning("No host genes passed min_cells=%d filter.", min_cells)
        return pd.DataFrame(columns=["gene", "correlation", "p_value", "adjusted_p"])

    results = []
    total_genes = host_adata.n_vars

    X = host_adata.X
    if sparse.issparse(X):
        # CSC slicing is significantly faster for repeated per-column access.
        X = X.tocsc()

    start_time = time.perf_counter()
    logger.info(
        "Starting host-virus interaction correlation loop for selected gene '%s' across %d host genes.",
        selected_gene,
        total_genes,
    )

    for i, gene in enumerate(host_adata.var_names, start=1):

        expression = X[:, i - 1]

        if hasattr(expression, "toarray"):
            expression = expression.toarray().ravel()
        else:
            expression = np.asarray(expression).ravel()

        if expression.size == 0 or np.nanstd(expression) == 0:
            continue

        corr, p = spearmanr(
            viral_expression,
            expression,
            nan_policy="omit",
        )

        if np.isnan(corr):
            continue

        results.append({
            "gene": gene,
            "correlation": corr,
            "p_value": p,
        })

        if i % 500 == 0 or i == total_genes:
            elapsed = time.perf_counter() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total_genes - i) / rate if rate > 0 else float("inf")
            logger.info(
                "Host-virus interaction progress: %d/%d genes (%.1f%%). Elapsed %.1fs. ETA %.1fs.",
                i,
                total_genes,
                (i / total_genes) * 100 if total_genes else 100.0,
                elapsed,
                remaining if np.isfinite(remaining) else -1,
            )

    if not results:
        results = pd.DataFrame(columns=["gene", "correlation", "p_value", "adjusted_p"])
        if "host_virus_interactions" not in adata.uns:
            adata.uns["host_virus_interactions"] = {}
        adata.uns["host_virus_interactions"][selected_gene] = results
        return results

    results = pd.DataFrame(results)

    results["adjusted_p"] = multipletests(
        results["p_value"],
        method="fdr_bh",
    )[1]

    results = results.sort_values(
        "correlation",
        ascending=False,
    ).reset_index(drop=True)

    if "host_virus_interactions" not in adata.uns:
        adata.uns["host_virus_interactions"] = {}

    adata.uns["host_virus_interactions"][selected_gene] = results

    logger.info(
        "Completed host-virus interaction for '%s'. Tested genes: %d. Returned genes: %d.",
        selected_gene,
        total_genes,
        len(results),
    )

    return results