from viral_platform.state.dataset_store import get_dataset
import logging
import decoupler as dc
from anndata import AnnData

logger = logging.getLogger(__name__)



def subset_cells(grouping, group1, group2, celltype="All Cells"):
    """
    Subset the working dataset based on the selected grouping variable, groups, and cell type.
    
    Parameters:
    - grouping: The metadata column to group by.
    - group1: The first group to include in the subset.
    - group2: The second group to include in the subset.
    - celltype: The cell type to filter by (if provided).
    
    Returns:
    - A new AnnData object containing only the cells that match the specified criteria.
    """
    adata = get_dataset()
    if adata is None:
        logger.warning("No working dataset available for subsetting.")
        return None
    
    if group1 == group2:
        logger.warning("Group 1 and Group 2 are the same. No subsetting performed.")
        return None
    
    # Filter by grouping variable and groups
    if grouping and group1 and group2:
        adata = adata[adata.obs[grouping].isin([group1, group2])]
    
    # Filter by cell type if provided
    if celltype and celltype != "All Cells":
        adata = adata[adata.obs['cell_type'] == celltype]
    
    print(adata)
    print(adata.obs[grouping].value_counts())
    
    return adata

def find_biological_replicates(adata, grouping):
    """
    Check for biological replicates in the dataset based on the specified grouping variable.

    Parameters:
    - adata: The AnnData object containing the dataset.
    - grouping: The metadata column to group by for identifying biological replicates.

    Returns:
    - A pandas Series indicating the number of unique samples for each group in the specified grouping variable
    """
    continue_analysis = False
    sample_column = "sampleID" # temprorary hardcoded value, should be dynamic based on metadata discovery
    if adata is None or grouping not in adata.obs.columns:
        logger.warning("Invalid dataset or grouping variable for finding biological replicates.")
        return continue_analysis
    
    # Assuming that biological replicates are identified by unique values in the grouping column
    biological_replicates = adata.obs.groupby(grouping)[sample_column].nunique()
    print(biological_replicates)

    min_replicates = 2
    if (biological_replicates < min_replicates).any():
        logger.warning("Some groups have fewer than %d biological replicates. Cannot perform pseudobulk.", min_replicates)
        return continue_analysis
    else:
        logger.info("Proceeding with pseudobulk. All groups have at least %d biological replicates.", min_replicates)
        continue_analysis = True
    
    return continue_analysis

def create_pseudobulk(adata, grouping, sample_column="sampleID"):
    """
    Create a pseudobulk dataset from the given AnnData object based on the specified grouping variable and sample column.

    Parameters:
    - adata: The AnnData object containing the dataset.
    - grouping: The metadata column to group by for creating pseudobulk.
    - sample_column: The metadata column that identifies individual samples (default is "sampleID").

    Returns:
    - A new AnnData object representing the pseudobulk dataset.
    """
    if adata is None or grouping not in adata.obs.columns or sample_column not in adata.obs.columns:
        logger.warning("Invalid dataset or grouping/sample columns for creating pseudobulk.")
        return None
    
    adata = check_adata_type(adata)
    padata = dc.pp.pseudobulk(adata, sample_col=sample_column, groups_col=grouping)

    logger.info("Pseudobulk dataset created with %d groups based on '%s' and '%s'.", padata.n_obs, grouping, sample_column)
    #print(padata)
    #print(padata.obs.head())
    #print(padata.obs["sampleID"].nunique())
    #print(padata.obs.groupby("CoVID-19 severity").size())
    return padata

def check_adata_type(adata):
    if adata.X.dtype == 'float32':
        adata_pb = AnnData(
            X=adata.raw.X.copy(),
            obs=adata.obs.copy(),
            var=adata.raw.var.copy(),
            )
        return adata_pb
    return adata