import logging
import os
import re
import tempfile
import zipfile
from pathlib import Path
import anndata as ad
import pandas as pd
import scanpy as sc

from viral_platform.state.dataset_store import set_dataset, set_working_dataset
from viral_platform.analysis.metadata import discover_metadata

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────────────
# ────── 10x zip loading ─────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────────────────────────

# Matches any matrix.mtx or matrix.mtx.gz file, capturing any prefix before "matrix".
MATRIX_FILENAME_PATTERN = re.compile(r"^(?P<prefix>.+)matrix\.mtx(?:\.gz)?$", re.IGNORECASE)

# Each tuple lists acceptable filename variants for one required 10x file type.
REQUIRED_10X_FILES = (
    ("matrix.mtx", "matrix.mtx.gz"),
    ("barcodes.tsv", "barcodes.tsv.gz"),
    ("features.tsv", "features.tsv.gz", "genes.tsv", "genes.tsv.gz"),
)

PREFIXED_BARCODES_SUFFIXES = ("barcodes.tsv.gz", "barcodes.tsv")
PREFIXED_FEATURES_SUFFIXES = ("features.tsv.gz", "features.tsv", "genes.tsv.gz", "genes.tsv")


# ── Shared post-processing ────────────────────────────────────────────────────

def _postprocess_loaded_adata(adata, sample_count=None):
    """
    High-level helper for ass successful loads.
    Input: An AnnData object and an optional sample count
    Output: The same AnnData Object after dataset-store updates and QC metric initialization.
    Interacts with set_dataset, set_working_dataset, and Scanpy QC metric calculation
    """
    set_dataset(adata)

    if sample_count is not None:
        adata.uns["sample_count"] = int(sample_count)

    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-") # Annotate mitochondrial genes
    adata.var["mt"] = (
        adata.var["mt"].fillna(False).astype(bool)
    )
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)
    set_working_dataset(adata)

    # Temporary
    # print(adata.obs.columns)
    import numpy as np

    X = adata.raw.X

    if hasattr(X, "data"):  # sparse matrix
        values = X.data
    else:
        values = X.ravel()

    print("Min:", values.min())
    print("Max:", values.max())
    print("Non-integer values:", np.sum(values != np.floor(values)))

    # end temporary
    discover_metadata(adata)
    #history = get_state_store()
    #print("Metadata info after discovery:", history.get("metadata_info", {}))
    return adata


# ── Zip extraction ────────────────────────────────────────────────────────────

def _safe_extract_zip(zip_path, destination_dir):
    """
    Safely extract an uploaded zip archive into a temporary directory
    Input: Path to the zip file and destination directory
    Output: None
    Interacts with _load_10x_zip, which uses extracted contents for 10x discovery and loading
    """
    destination_root = Path(destination_dir).resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = Path(member.filename)
            if member_path.is_absolute():
                raise ValueError(f"Unsafe absolute path in zip: {member.filename}")
            resolved = (destination_root / member_path).resolve()
            if resolved != destination_root and destination_root not in resolved.parents:
                raise ValueError(f"Unsafe path traversal in zip: {member.filename}")
        zf.extractall(destination_root)


# ── 10x helper utilities ──────────────────────────────────────────────────────

def _extract_prefix(filename):
    """Return the sample prefix from a *matrix.mtx(.gz) filename, or None."""
    m = MATRIX_FILENAME_PATTERN.match(filename)
    return m.group("prefix") if m else None


def _find_matching_file(directory, candidates):
    """Return the first existing Path from *candidates* inside *directory*, or None."""
    base = Path(directory)
    return next((p for name in candidates if (p := base / name).exists()), None)


# ── Per-sample prefixed 10x loading ──────────────────────────────────────────

def _load_prefixed_10x_sample(matrix_path):
    """Load one GEO-style prefixed 10x sample (any *matrix.mtx[.gz]) into AnnData."""
    matrix_path = Path(matrix_path)
    prefix = _extract_prefix(matrix_path.name)
    if prefix is None:
        raise ValueError(f"Could not infer sample prefix from: {matrix_path.name}")

    sample_dir = matrix_path.parent
    barcodes_path = _find_matching_file(
        sample_dir, [f"{prefix}{s}" for s in PREFIXED_BARCODES_SUFFIXES]
    )
    features_path = _find_matching_file(
        sample_dir, [f"{prefix}{s}" for s in PREFIXED_FEATURES_SUFFIXES]
    )

    # Collect any missing companions before raising so the error is fully informative.
    missing = []
    if barcodes_path is None:
        missing.append(f"{prefix}barcodes.tsv(.gz)")
    if features_path is None:
        missing.append(f"{prefix}features.tsv(.gz) / {prefix}genes.tsv(.gz)")
    if missing:
        raise ValueError(
            f"Missing required 10x files for prefix '{prefix}': {', '.join(missing)}"
        )

    logger.info("Loading 10x sample '%s' from %s.", prefix, matrix_path)

    matrix = sc.read_mtx(str(matrix_path))
    barcodes = pd.read_csv(barcodes_path, header=None, sep="\t").iloc[:, 0].astype(str).tolist()
    feature_table = pd.read_csv(features_path, header=None, sep="\t")
    # Use the second column (gene symbols) when available, otherwise fall back to the first.
    gene_names = feature_table.iloc[:, 1 if feature_table.shape[1] >= 2 else 0].astype(str).tolist()

    adata = ad.AnnData(matrix.T)
    adata.obs_names, adata.var_names = barcodes, gene_names
    adata.obs["sample_id"] = prefix
    adata.obs_names_make_unique()
    adata.var_names_make_unique()
    return adata


def _load_prefixed_10x_samples(root_dir):
    """Discover all prefixed 10x samples under *root_dir* and concatenate them.

    Returns a combined AnnData, or None when no prefixed matrix files are found.
    """
    root_path = Path(root_dir)

    # Collect and sort matrix files so sample order is deterministic.
    matrix_paths = sorted(
        (p for p in root_path.rglob("*") if p.is_file() and _extract_prefix(p.name) is not None),
        key=lambda p: (str(p.parent), p.name),
    )
    if not matrix_paths:
        return None

    sample_adatas = [_load_prefixed_10x_sample(p) for p in matrix_paths]
    # _extract_prefix is guaranteed non-None here because of the filter above.
    sample_names = [_extract_prefix(p.name) for p in matrix_paths]

    logger.info("Loaded %d prefixed 10x sample(s) from zip archive.", len(sample_adatas))

    combined = (
        sample_adatas[0]
        if len(sample_adatas) == 1
        else ad.concat(
            sample_adatas,
            join="outer",
            label="sample_id",
            keys=sample_names,
            index_unique="-",
        )
    )
    combined.uns["sample_count"] = len(sample_adatas)
    return combined


# ── Standard (unprefixed) 10x directory discovery ────────────────────────────

def _find_10x_directory(root_dir):
    """Walk *root_dir* and return the shallowest directory that contains all
    required 10x files, or None if no such directory exists."""
    root_path = Path(root_dir)
    candidates = [
        Path(dirpath)
        for dirpath, _, files in os.walk(root_path)
        if all(
            any(opt in {f.lower() for f in files} for opt in group)
            for group in REQUIRED_10X_FILES
        )
    ]
    if not candidates:
        return None
    # Prefer the shallowest match to avoid accidentally picking up nested artefacts.
    return min(candidates, key=lambda p: len(p.relative_to(root_path).parts))

# ──────────────────────────────────────────────────────────────────────────────────
# ──── End of 10x zip loading code ─────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────────


# ── Top-level format loaders ──────────────────────────────────────────────────

def _load_h5ad(path):
    """Read an h5ad file and run shared post-processing."""
    return _postprocess_loaded_adata(sc.read_h5ad(path), sample_count=1)


def _load_10x_zip(path):
    """Extract a zip archive and load either prefixed GEO-style samples or a
    standard 10x directory, then run shared post-processing."""
    with tempfile.TemporaryDirectory(prefix="tenx_zip_") as tmp:
        logger.info("Extracting 10x zip archive %s.", path)
        _safe_extract_zip(path, tmp)

        # Try prefixed (GEO-style) layout first.
        adata = _load_prefixed_10x_samples(tmp)
        if adata is not None:
            logger.info(
                "Concatenated prefixed samples: %d cells, %d genes.",
                adata.n_obs, adata.n_vars,
            )
            return _postprocess_loaded_adata(adata)

        # Fall back to a standard unprefixed 10x directory.
        tenx_dir = _find_10x_directory(tmp)
        if tenx_dir is None:
            raise ValueError(
                "Zip does not contain a valid 10x directory. "
                "Expected: matrix.mtx(.gz), barcodes.tsv(.gz), features/genes.tsv(.gz)."
            )

        logger.info("Detected standard 10x directory at %s.", tenx_dir)
        return _postprocess_loaded_adata(
            sc.read_10x_mtx(str(tenx_dir), var_names="gene_symbols", make_unique=True),
            sample_count=1,
        )


# Map file extensions to their loader functions; extend here as new formats are added.
LOADER_BY_EXTENSION = {
    ".h5ad": _load_h5ad,
    ".zip":  _load_10x_zip,
}


# ── Public entry point ────────────────────────────────────────────────────────

def load_file_from_path(file_path):
    """Normalise *file_path*, select the correct loader by extension, and return
    a post-processed AnnData object. Raises ValueError / FileNotFoundError for
    bad input and RuntimeError if loading or preprocessing fails."""
    if not file_path:
        raise ValueError("No file path provided.")

    normalized = os.path.expanduser(file_path.strip().strip('"'))

    if not os.path.exists(normalized):
        raise FileNotFoundError(f"File not found: {normalized}")

    ext = Path(normalized).suffix.lower()
    loader = LOADER_BY_EXTENSION.get(ext)
    if loader is None:
        supported = ", ".join(sorted(LOADER_BY_EXTENSION))
        raise ValueError(
            f"Unsupported file type '{ext or '[none]'}'. Supported: {supported}"
        )

    try:
        logger.info("Loading '%s' with loader for '%s'.", normalized, ext)
        adata = loader(normalized)
        logger.info(
            "Loaded %d cells × %d genes from '%s'.", adata.n_obs, adata.n_vars, normalized
        )
        return adata
    except Exception as exc:
        logger.exception("Failed to load '%s'.", normalized)
        raise RuntimeError(f"Could not process '{normalized}': {exc}") from exc