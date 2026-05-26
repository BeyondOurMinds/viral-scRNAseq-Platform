import os
import scanpy as sc


def load_h5ad_from_path(file_path):
    if not file_path:
        raise ValueError("No file path provided.")

    normalized_path = os.path.expanduser(file_path.strip().strip('"'))

    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"File not found: {normalized_path}")

    if not normalized_path.lower().endswith(".h5ad"):
        raise ValueError("Only .h5ad files are supported.")

    adata = sc.read_h5ad(normalized_path)
    print(f"Loaded h5ad from path with {adata.n_obs} cells and {adata.n_vars} genes.")
    return adata

