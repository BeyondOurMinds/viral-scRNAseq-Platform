import os
import scanpy as sc

from viral_platform.state.dataset_store import set_dataset, set_working_dataset

# Utility function to load accepted file types from a given file path, with error handling.
# This is used by the upload callback to read the uploaded file and return an AnnData object.
# It checks for file existence, correct extension, and handles exceptions during loading.
# The function normalizes the file path to handle user input variations and provides informative error messages if issues arise.
def load_file_from_path(file_path):
    if not file_path:
        raise ValueError("No file path provided.")

    normalized_path = os.path.expanduser(file_path.strip().strip('"'))

    if not os.path.exists(normalized_path):
        raise FileNotFoundError(f"File not found: {normalized_path}")
    
    if normalized_path.lower().endswith(".h5ad"):
        adata = sc.read_h5ad(normalized_path)
        print(f"Loaded h5ad from path with {adata.n_obs} cells and {adata.n_vars} genes.")
        print(normalized_path)
        set_dataset(adata)

        # Mark mitochondrial genes so scanpy computes pct_counts_mt.
        adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
        sc.pp.calculate_qc_metrics(
            adata,
            qc_vars=["mt"],
            inplace=True,
        )
        set_working_dataset(adata)
        
        return adata

    return None

