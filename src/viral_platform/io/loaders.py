import os
import logging
import scanpy as sc

from viral_platform.state.dataset_store import set_dataset, set_working_dataset

logger = logging.getLogger(__name__)


def _load_h5ad(normalized_path):
    adata = sc.read_h5ad(normalized_path)
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


# Register extension-based loaders here as support is added.
LOADER_BY_EXTENSION = {
    ".h5ad": _load_h5ad,
}

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

    _, extension = os.path.splitext(normalized_path)
    extension = extension.lower()
    loader = LOADER_BY_EXTENSION.get(extension)
    if loader is None:
        supported_types = ", ".join(sorted(LOADER_BY_EXTENSION.keys()))
        raise ValueError(
            f"Unsupported file type '{extension or '[none]'}'. Supported types: {supported_types}"
        )

    try:
        logger.info("Loading dataset from %s using loader for extension '%s'.", normalized_path, extension)
        adata = loader(normalized_path)
        logger.info(
            "Loaded dataset from %s with %s cells and %s genes.",
            normalized_path,
            adata.n_obs,
            adata.n_vars,
        )
        logger.info("Post-load processing completed for %s.", normalized_path)
        return adata
    except Exception as exc:
        logger.exception("Failed to load or preprocess uploaded file: %s", normalized_path)
        raise RuntimeError(f"Could not process file '{normalized_path}': {exc}") from exc

