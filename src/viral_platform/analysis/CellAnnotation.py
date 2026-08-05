import celltypist as ct
from celltypist import models
import scanpy as sc


def annotate_cells(
    adata,
    model_name="Immune_All_Low.pkl",
    majority_voting=True,
):
    """
    Annotate cells using CellTypist.

    Parameters
    ----------
    adata : AnnData
        AnnData object to annotate.

    model_name : str
        CellTypist model filename.

    majority_voting : bool
        Whether to perform cluster-based majority voting.

    Returns
    -------
    AnnData
        Updated AnnData object with SCJoseki annotation columns.
    """

    # Load CellTypist model
    model = models.Model.load(model_name)

    # Run CellTypist
    predictions = ct.annotate(
        adata,
        model=model,
        majority_voting=majority_voting
    )

    # Store per-cell predictions
    adata.obs["SCJoseki_predicted_celltype"] = (
        predictions.predicted_labels["predicted_labels"].values
    )

    # Store confidence scores (if available)
    if "conf_score" in predictions.predicted_labels.columns:
        adata.obs["SCJoseki_confidence"] = (
            predictions.predicted_labels["conf_score"].values
        )

    # Store majority-voted labels
    if majority_voting and hasattr(predictions, "majority_voting"):
        adata.obs["SCJoseki_majority_celltype"] = (
            predictions.majority_voting["majority_voting"].values
        )

    return adata

def celltypist_umap(adata, color_by="SCJoseki_majority_celltype"):
    # Determine which metadata column to colour by
    if color_by in adata.obs.columns:
        color_column = color_by
    else:
        color_column = "leiden"

    fig = sc.pl.umap(
        adata,
        color=color_column,
        legend_loc="on data",
        legend_fontsize=10,
        frameon=False,
        return_fig=True,
    )
    return fig