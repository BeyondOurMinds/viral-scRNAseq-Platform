import pandas as pd

from viral_platform.state.dataset_store import update_state_store
from viral_platform.utils.sample_column_utils import (
    is_sample_named_column,
    looks_like_identifier_column,
    rank_sample_columns,
)


def _is_groupable_metadata_column(series):
    """Return True for metadata columns suitable for grouping in UI dropdowns."""
    return (
        pd.api.types.is_categorical_dtype(series)
        or pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
        or pd.api.types.is_bool_dtype(series)
    )


def _extract_unique_non_empty_values(series):
    """Return ordered, non-empty string values for dropdown-style metadata use."""
    values = series.dropna().astype(str).tolist()
    seen = set()
    unique_values = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(normalized)
    return unique_values


def _is_too_high_cardinality(series, *, unique_ratio_threshold=0.98, unique_count_floor=1000):
    """Return True for columns that are effectively one-identifier-per-cell."""
    non_null = series.dropna()
    if non_null.empty:
        return False
    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = unique_count / float(len(non_null))
    return unique_count >= unique_count_floor and unique_ratio >= unique_ratio_threshold


def discover_metadata(adata):
    """
    Discover and store metadata information from the AnnData object.
    This function identifies groupable columns, cell type columns, and sample columns.
    """
    if adata is None:
        return

    metadata_info_new = {
        "groupable_columns": [],
        "cell_type_columns": [],
        "cell_types": ["All Cells"],
        "sample_columns": [],
    }

    #cell_type_list = []
    #celltype_list = []
    #majortype_list = []


    # Identify columns suitable for grouping/dropdowns.
    for col in adata.obs.columns:
        column_name = str(col)
        series = adata.obs[col]
        if not _is_groupable_metadata_column(series):
            continue

        is_sample_column = is_sample_named_column(column_name)

        # Skip columns that behave like cell-level identifiers.
        if looks_like_identifier_column(column_name) and not is_sample_column:
            continue
        if _is_too_high_cardinality(series) and not is_sample_column:
            continue

        metadata_info_new["groupable_columns"].append(col)
    
    # if "cell_type" in adata.obs.columns.lower() or "celltype" in adata.obs.columns.lower():
    #     metadata_info_new["cell_types"].extend(adata.obs["cell_type"].cat.categories.tolist())

    # Identify specific types of metadata based on naming conventions
    for col in metadata_info_new["groupable_columns"]:
        if "cell_type" in col.lower() or "celltype" in col.lower() or "cell type" in col.lower():
            metadata_info_new["cell_type_columns"].append(col)
            metadata_info_new["cell_types"].extend(
                _extract_unique_non_empty_values(adata.obs[col])
            )
            '''if "cell_type" in col.lower():
                cell_type_list.append(adata.obs[col].cat.categories.tolist())
            elif "celltype" in col.lower():
                celltype_list.append(adata.obs[col].cat.categories.tolist())
            elif "majortype" in col.lower():
                majortype_list.append(adata.obs[col].cat.categories.tolist())'''
    # Detect sample columns independently from groupability filters so
    # sample-like names (e.g., Sample_geo_accession) are always discoverable.
    metadata_info_new["sample_columns"] = rank_sample_columns(
        adata.obs.columns,
        obs_df=adata.obs,
        min_score=1,
    )

    # Keep deterministic order while removing duplicates.
    metadata_info_new["groupable_columns"] = list(
        dict.fromkeys(metadata_info_new["groupable_columns"])
    )
    metadata_info_new["cell_type_columns"] = list(
        dict.fromkeys(metadata_info_new["cell_type_columns"])
    )
    metadata_info_new["sample_columns"] = list(
        dict.fromkeys(metadata_info_new["sample_columns"])
    )
    metadata_info_new["cell_types"] = list(dict.fromkeys(metadata_info_new["cell_types"]))

    # Update the state store with discovered metadata information
    #state = get_state_store()
    #state["metadata_info"] = metadata_info_new
    #print("cell_type_list:", cell_type_list)
    #print("celltype_list:", celltype_list)
    #print("majortype_list:", majortype_list)
    update_state_store(metadata_info=metadata_info_new)