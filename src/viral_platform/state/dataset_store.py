_DEFAULT_HISTORY = {
    "raw": None,
    "working": None,
    "metadata": False,
    "nFeature_RNA": {"min": None, "max": None},
    "nCount_RNA": {"min": None, "max": None},
    "percent_mt": None,
    "has_cols": [],
    "metadata_info": {
        "groupable_columns": [],
        "cell_type_columns": [],
        "cell_types": [],
        "sample_columns": [],
    },
    "viral_detection": {
        "viral_genes": [],
        "viral_features": [],
    }
}


def _new_history_state():
    """Create a fresh default state object for one user session."""
    return {
        "raw": None,
        "working": None,
        "metadata": False,
        "nFeature_RNA": {"min": None, "max": None},
        "nCount_RNA": {"min": None, "max": None},
        "percent_mt": None,
        "has_cols": [],
        "metadata_info": {
            "groupable_columns": [],
            "cell_type_columns": [],
            "cell_types": [],
            "sample_columns": [],
        },
        "viral_detection": {
            "viral_genes": [],
            "viral_features": [],
        }
    }


history = _new_history_state()


def get_state_store():
    """Expose the shared in-memory state dictionary for cross-module access."""
    return history


def reset_state_store():
    """Reset the shared state back to defaults between uploads or sessions."""
    history.clear()
    history.update(_new_history_state())


def update_state_store(**kwargs):
    """Safely update known top-level state keys in one call."""
    for key, value in kwargs.items():
        if key not in _DEFAULT_HISTORY:
            raise KeyError(f"Unknown dataset state key: {key}")
        history[key] = value


def _as_float(value):
    """Convert values from pandas/NumPy scalars to float for lightweight state storage."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sync_state_with_dataset(adata):
    """Refresh state metadata and QC bounds from the current AnnData object."""
    if adata is None:
        return

    columns = list(adata.obs.columns)
    history["has_cols"] = columns
    history["metadata"] = bool(columns)

    if "nFeature_RNA" in adata.obs:
        history["nFeature_RNA"] = {
            "min": _as_float(adata.obs["nFeature_RNA"].min()),
            "max": _as_float(adata.obs["nFeature_RNA"].max()),
        }

    if "nCount_RNA" in adata.obs:
        history["nCount_RNA"] = {
            "min": _as_float(adata.obs["nCount_RNA"].min()),
            "max": _as_float(adata.obs["nCount_RNA"].max()),
        }

    if "percent.mt" in adata.obs:
        history["percent_mt"] = _as_float(adata.obs["percent.mt"].max())


def set_dataset(adata):
    """Store the raw/original dataset and refresh derived state metadata."""
    history["raw"] = adata
    sync_state_with_dataset(adata)


def get_dataset():
    """Return the raw/original dataset for the active session."""
    return history["raw"]


def clear_dataset():
    """Clear only the raw/original dataset reference from state."""
    history["raw"] = None


def set_working_dataset(adata):
    """Store the current working dataset and refresh derived state metadata."""
    history["working"] = adata
    sync_state_with_dataset(adata)


def get_working_dataset():
    """Return the currently active working dataset."""
    return history["working"]


def clear_working_dataset():
    """Clear the working dataset and reset derived state values."""
    history["working"] = None
    history["metadata"] = False
    history["nFeature_RNA"] = {"min": None, "max": None}
    history["nCount_RNA"] = {"min": None, "max": None}
    history["percent_mt"] = None
    history["has_cols"] = []
    history["metadata_info"] = {
        "groupable_columns": [],
        "cell_type_columns": [],
        "cell_types": [],
        "sample_columns": [],
    }
    history["viral_detection"] = {
        "viral_genes": [],
        "viral_features": [],
    }