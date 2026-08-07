_DEFAULT_HISTORY = {
    "raw": None,
    "working": None,
    "adata_pca": None,
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
    "DE_results": {
        "results_by_celltype": {},
    },
    "viral_detection": {
        "viral_genes": [],
        "viral_features": [],
    },
    "isg_detection": {
        "isg_genes": [],
        "isg_features": [],
    },
    "CCC_results": {
        "results": None,
    },
    "CCC_reference_results": {
        "results": None,
        "file_type": None,
        "selected_filename": None,
    },
    "CCC_active_context": "uploaded",
    # Rendered Dash components are kept separately from AnnData so routed pages can be rebuilt without discarding plots and tables produced on another page.
    "results_cache": {},
}


def _new_history_state():
    """Create a fresh default state object for one user session."""
    return {
        "raw": None,
        "working": None,
        "adata_pca": None,
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
        "DE_results": {
            "results_by_celltype": {},
        },
        "viral_detection": {
            "viral_genes": [],
            "viral_features": [],
        },
        "isg_detection": {
            "isg_genes": [],
            "isg_features": [],
        },
        "CCC_results": {
            "results": None,
        },
        "CCC_reference_results": {
            "results": None,
            "file_type": None,
            "selected_filename": None,
        },
        "CCC_active_context": "uploaded",
        "results_cache": {},
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


def cache_results(**results):
    """Cache rendered result components by stable container ID.

    Dash Pages recreates a page's layout whenever it is revisited.  Keeping the
    components in the shared, dataset-scoped state allows the corresponding
    layout factory to repopulate its containers on remount.
    """
    history["results_cache"].update(results)


def get_cached_result(result_id, default=None):
    """Return a cached result component, or the panel's normal placeholder."""
    return history["results_cache"].get(result_id, default)


def clear_results_cache():
    """Remove generated UI results, normally when a new dataset is loaded."""
    history["results_cache"] = {}


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

    # Metadata columns can be introduced by any analysis module (for example,
    # cell annotation adds predicted-cell-type fields).  Refresh discovery here
    # rather than only after upload so every metadata-driven dropdown sees the
    # current AnnData ``obs`` schema when its page is mounted.
    from viral_platform.analysis.metadata import discover_metadata

    discover_metadata(adata)


def set_dataset(adata):
    """Store the raw/original dataset and refresh derived state metadata."""
    history["raw"] = adata
    history["adata_pca"] = None
    clear_results_cache()
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


def set_pca_dataset(adata_pca):
    """Store the PCA-ready AnnData object derived from the working dataset."""
    history["adata_pca"] = adata_pca


def get_pca_dataset():
    """Return the PCA-ready AnnData object for the active session."""
    return history["adata_pca"]


def clear_pca_dataset():
    """Clear the PCA-ready AnnData object from state."""
    history["adata_pca"] = None


def get_working_dataset():
    """Return the currently active working dataset."""
    return history["working"]


def clear_working_dataset():
    """Clear the working dataset and reset derived state values."""
    history["working"] = None
    history["adata_pca"] = None
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
    history["DE_results"] = {
        "results_by_celltype": {},
    }
    history["viral_detection"] = {
        "viral_genes": [],
        "viral_features": [],
    }
    history["isg_detection"] = {
        "isg_genes": [],
        "isg_features": [],
    }
    history["CCC_results"] = {
        "results": None,
    }
    history["CCC_reference_results"] = {
        "results": None,
        "file_type": None,
        "selected_filename": None,
    }
    history["CCC_active_context"] = "uploaded"
    clear_results_cache()
