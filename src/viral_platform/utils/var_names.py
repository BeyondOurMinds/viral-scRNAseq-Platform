import logging
import liana as li

logger = logging.getLogger(__name__)

COMMON_SYMBOL_COLUMNS = [
    "feature_name",
    "gene_name",
    "gene_symbol",
    "symbol",
    "GeneSymbol",
    "gene",
    "gene_symbols",
]



def ensure_gene_symbols(adata, selected_resource="consensus"):
    """
    Ensure that the AnnData object has gene symbols as var_names.

    Parameters
    ----------
    adata : AnnData
        The input AnnData object containing single-cell data.
    selected_resource : str, optional
        The resource to use for ligand-receptor interactions. Default is "consensus".

    Returns
    -------
    AnnData
        The AnnData object with gene symbols as var_names.
    """

    resource = li.rs.select_resource(selected_resource)
    resource_genes = (
        set(resource["ligand"])
        | set(resource["receptor"])
    )

    best_coverage = liana_gene_coverage(
        adata.var_names, resource_genes
    )

    best_column = None

    for col in COMMON_SYMBOL_COLUMNS:
        if col not in adata.var.columns:
            continue

        coverage = liana_gene_coverage(
            adata.var[col].astype(str),
            resource_genes
        )

        if coverage > best_coverage:
            best_coverage = coverage
            best_column = col

    if best_coverage < 0.1:
        logger.warning(
            "Low coverage of gene symbols in adata.var. "
            "Best coverage: %.2f%%. Consider providing a column with gene symbols.",
            best_coverage * 100
        )
        raise ValueError(
            "Low coverage of gene symbols in adata.var. "
            "Best coverage: %.2f%%." % (best_coverage * 100)
        )

    if best_column is not None:
        logger.info(
            "Using '%s' column in adata.var for gene symbols. Coverage: %.2f%%",
            best_column, best_coverage * 100
        )
        
        orig_var_names = adata.var_names.copy()
        adata.uns["original_var_names"] = orig_var_names

        logger.info(
            "Original var_names stored in adata.uns['original_var_names']."
        )

        adata.var_names = adata.var[best_column].astype(str)
        adata.var_names_make_unique()
        return adata
    else:
        logger.warning(
            "No suitable gene symbol column found in adata.var. "
            "Using existing var_names. Coverage: %.2f%%",
            best_coverage * 100
        )
        return adata
def liana_gene_coverage(gene_names, resource_genes):
    gene_names = set(map(str, gene_names))
    return len(gene_names & resource_genes) / len(resource_genes)