import scanpy as sc
from viral_platform.state.dataset_store import get_working_dataset, set_working_dataset
import logging


logger = logging.getLogger(__name__)

def preprocess_data():
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for preprocessing.")
    
    try:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)

        # Preserve log-normalized expression for downstream analyses (e.g. CCC).
        adata.layers["log_normalized"] = adata.X.copy()

        sc.pp.scale(adata, max_value=10)

        # Keep scaled values accessible while PCA/clustering continue to use adata.X.
        adata.layers["scaled"] = adata.X.copy()

        set_working_dataset(adata)
        run_pca()
        logger.info("Preprocessing completed successfully.")
    except Exception as exc:
        logger.exception("Preprocessing failed: %s", str(exc))
        raise RuntimeError("Preprocessing failed: " + str(exc)) from exc

def run_pca():
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for PCA.")
    
    try:
        sc.tl.pca(adata, svd_solver="arpack")
        set_working_dataset(adata)
        logger.info("PCA completed successfully.")
    except Exception as exc:
        logger.exception("PCA failed: %s", str(exc))
        raise RuntimeError("PCA failed: " + str(exc)) from exc
    
def run_clustering(n_dims=10):
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for clustering.")
    
    try:
        sc.pp.neighbors(adata, n_neighbors=10, n_pcs=n_dims)
        sc.tl.leiden(adata)
        sc.tl.umap(adata)
        set_working_dataset(adata)
        logger.info("Clustering completed successfully.")
    except Exception as exc:
        logger.exception("Clustering failed: %s", str(exc))
        raise RuntimeError("Clustering failed: " + str(exc)) from exc