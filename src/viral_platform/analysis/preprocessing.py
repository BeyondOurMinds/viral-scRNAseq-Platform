import scanpy as sc
from viral_platform.state.dataset_store import (
    get_working_dataset,
    set_working_dataset,
    set_pca_dataset,
    get_pca_dataset,
)
import logging


logger = logging.getLogger(__name__)

def preprocess_data():
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for preprocessing.")
    
    try:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

        # Preserve log-normalized expression for downstream analyses (e.g. CCC).
        adata.layers["log_normalized"] = adata.X.copy()

        sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=False)

        adata_pca = adata[:, adata.var.highly_variable].copy()
        sc.pp.scale(adata_pca, max_value=10)
        set_pca_dataset(adata_pca)

        # Keep scaled values accessible while PCA/clustering continue to use adata.X.
        # adata.layers["scaled"] = adata_pca.X.copy()

        set_working_dataset(adata)
        run_pca()
        logger.info("Preprocessing completed successfully.")
    except Exception as exc:
        logger.exception("Preprocessing failed: %s", str(exc))
        raise RuntimeError("Preprocessing failed: " + str(exc)) from exc

def run_pca():
    adata = get_working_dataset()
    adata_pca = get_pca_dataset()
    if adata is None:
        raise ValueError("No active dataset found for PCA.")
    if adata_pca is None:
        raise ValueError("No PCA-ready dataset found. Run preprocessing first.")
    
    try:
        sc.tl.pca(adata_pca, svd_solver="arpack")

        # Mirror PCA outputs back to the main AnnData object used by the app.
        adata.obsm["X_pca"] = adata_pca.obsm["X_pca"].copy()
        adata.uns["pca"] = adata_pca.uns["pca"].copy()

        set_pca_dataset(adata_pca)

        set_working_dataset(adata)
        logger.info("PCA completed successfully.")
    except Exception as exc:
        logger.exception("PCA failed: %s", str(exc))
        raise RuntimeError("PCA failed: " + str(exc)) from exc
    
def run_clustering(n_dims=10):
    adata = get_working_dataset()
    adata_pca = get_pca_dataset()
    if adata is None:
        raise ValueError("No active dataset found for clustering.")
    if adata_pca is None:
        raise ValueError("No PCA-ready dataset found. Run preprocessing/PCA first.")
    
    try:
        sc.pp.neighbors(adata_pca, n_neighbors=10, n_pcs=n_dims)
        sc.tl.leiden(adata_pca)
        sc.tl.umap(adata_pca)

        # Keep all downstream consumers reading from the canonical working object.
        adata.obsp["distances"] = adata_pca.obsp["distances"].copy()
        adata.obsp["connectivities"] = adata_pca.obsp["connectivities"].copy()
        adata.uns["neighbors"] = adata_pca.uns["neighbors"].copy()
        adata.obs["leiden"] = adata_pca.obs["leiden"].copy()
        adata.obsm["X_umap"] = adata_pca.obsm["X_umap"].copy()
        adata.uns["umap"] = adata_pca.uns["umap"].copy()

        set_pca_dataset(adata_pca)
        set_working_dataset(adata)
        logger.info("Clustering completed successfully.")
    except Exception as exc:
        logger.exception("Clustering failed: %s", str(exc))
        raise RuntimeError("Clustering failed: " + str(exc)) from exc