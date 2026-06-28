from viral_platform.state.dataset_store import update_state_store

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


    # Identify groupable columns (categorical columns)
    for col in adata.obs.columns:
        if adata.obs[col].dtype.name == 'category' or adata.obs[col].dtype.name == 'object':
            metadata_info_new["groupable_columns"].append(col)
    print(adata.obs.columns)
    
    # if "cell_type" in adata.obs.columns.lower() or "celltype" in adata.obs.columns.lower():
    #     metadata_info_new["cell_types"].extend(adata.obs["cell_type"].cat.categories.tolist())

    # Identify specific types of metadata based on naming conventions
    for col in metadata_info_new["groupable_columns"]:
        if "cell_type" in col.lower() or "celltype" in col.lower():
            metadata_info_new["cell_type_columns"].append(col)
            metadata_info_new["cell_types"].extend(adata.obs[col].cat.categories.tolist())
            '''if "cell_type" in col.lower():
                cell_type_list.append(adata.obs[col].cat.categories.tolist())
            elif "celltype" in col.lower():
                celltype_list.append(adata.obs[col].cat.categories.tolist())
            elif "majortype" in col.lower():
                majortype_list.append(adata.obs[col].cat.categories.tolist())'''
        elif "sample" in col.lower():
            metadata_info_new["sample_columns"].append(col)

    # Update the state store with discovered metadata information
    #state = get_state_store()
    #state["metadata_info"] = metadata_info_new
    #print("cell_type_list:", cell_type_list)
    #print("celltype_list:", celltype_list)
    #print("majortype_list:", majortype_list)
    update_state_store(metadata_info=metadata_info_new)