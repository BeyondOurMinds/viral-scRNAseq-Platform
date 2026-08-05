import celltypist as ct
from celltypist import models
import pandas as pd
import plotly.express as px
import logging

logger = logging.getLogger(__name__)


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
        Whether to perform CellTypist majority voting.

    Returns
    -------
    AnnData
        Updated AnnData object with CellTypist annotations stored in
        SCJoseki-specific metadata columns.
    """

    # Load CellTypist model
    model = models.Model.load(model_name)

    # Run CellTypist annotation
    predictions = ct.annotate(
        adata,
        model=model,
        majority_voting=majority_voting,
    )

    results = predictions.predicted_labels

    # Store per-cell predicted labels
    adata.obs["SCJoseki_predicted_celltype"] = (
        results["predicted_labels"].astype(str)
    )

    # Store confidence scores (if available)
    if "conf_score" in results.columns:
        adata.obs["SCJoseki_confidence"] = results["conf_score"]

    # Store CellTypist over-clustering assignments (optional)
    if "over_clustering" in results.columns:
        adata.obs["SCJoseki_overcluster"] = (
            results["over_clustering"].astype(str)
        )

    # Store majority-voted labels
    if majority_voting and "majority_voting" in results.columns:
        adata.obs["SCJoseki_majority_celltype"] = (
            results["majority_voting"].astype(str)
        )
    elif majority_voting:
        logger.warning(
            "CellTypist did not return a 'majority_voting' column. "
            "Falling back to per-cell predictions."
        )
        adata.obs["SCJoseki_majority_celltype"] = (
            results["predicted_labels"].astype(str)
        )

    return adata

def celltypist_umap(adata, color_by="SCJoseki_majority_celltype"):
    if "X_umap" not in adata.obsm:
        raise ValueError("UMAP coordinates are not available. Run clustering before plotting cell annotations.")

    # Determine which metadata column to color by, with safe fallbacks.
    if color_by in adata.obs.columns:
        color_column = color_by
        logger.info(f"Coloring UMAP by '{color_column}'.")
    elif "leiden" in adata.obs.columns:
        color_column = "leiden"
        logger.info("Coloring UMAP by 'leiden' clusters as fallback.")
    else:
        color_column = None
        logger.info("No valid color column found for UMAP. Plotting without color.")

    umap_df = pd.DataFrame(
        adata.obsm["X_umap"],
        columns=["UMAP1", "UMAP2"],
        index=adata.obs_names,
    )

    if color_column is not None:
        umap_df[color_column] = adata.obs[color_column].astype(str).fillna("Unknown").values
        fig = px.scatter(
            umap_df,
            x="UMAP1",
            y="UMAP2",
            color=color_column,
            title="CellTypist UMAP",
            labels={color_column: color_column},
        )
    else:
        fig = px.scatter(
            umap_df,
            x="UMAP1",
            y="UMAP2",
            title="CellTypist UMAP",
        )

    fig.update_traces(marker={"size": 5, "opacity": 0.8})
    fig.update_layout(
        template="plotly_white",
        xaxis_title="UMAP1",
        yaxis_title="UMAP2",
        legend_title_text=color_column if color_column is not None else "",
    )
    fig.update_layout(
            legend=dict(
                title="Cell Types",
                orientation="h",
                entrywidth=250,
                entrywidthmode="pixels",
                x=0.5,
                xanchor="center",
                y=-0.18,
                yanchor="top"
            ),
            margin=dict(b=140)
        )
    return fig