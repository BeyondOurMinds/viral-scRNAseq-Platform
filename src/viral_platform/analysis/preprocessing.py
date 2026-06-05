import scanpy as sc
from viral_platform.state.dataset_store import get_working_dataset, set_working_dataset

def preprocess_data():
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for preprocessing.")
    
    try:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=2000, subset=True)
        sc.pp.scale(adata, max_value=10)
        set_working_dataset(adata)
        run_pca()
    except Exception as exc:
        raise RuntimeError("Preprocessing failed: " + str(exc)) from exc

def run_pca():
    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No active dataset found for PCA.")
    
    try:
        sc.tl.pca(adata, svd_solver="arpack")
        set_working_dataset(adata)
    except Exception as exc:
        raise RuntimeError("PCA failed: " + str(exc)) from exc