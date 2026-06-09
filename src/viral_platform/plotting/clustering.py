import plotly.express as px
from viral_platform.state.dataset_store import get_working_dataset
import pandas as pd
from dash import dcc, html
import logging


logger = logging.getLogger(__name__)

def create_umap_plot(adata=None):
    if adata is None:
        adata = get_working_dataset()
    if adata is None:
        logger.warning("UMAP plot creation requested without an active dataset.")
        return html.Div("No dataset available for UMAP plot.")
    
    try:
        if "leiden" not in adata.obs.columns:
            logger.warning("UMAP plot creation requested but 'leiden' clustering not found in dataset.")
            return html.Div("Run clustering before creating UMAP plot.")
        
        umap_df = pd.DataFrame({
            "UMAP1": adata.obsm["X_umap"][:, 0],
            "UMAP2": adata.obsm["X_umap"][:, 1],
            "Cluster": adata.obs["leiden"].astype(str)
        })
        
        fig = px.scatter(
            umap_df,
            x="UMAP1",
            y="UMAP2",
            color="Cluster",
            title="UMAP Plot Colored by Leiden Clusters",
            labels={"Cluster": "Leiden Cluster"}
        )
        fig.update_layout(legend_title_text="Leiden Clusters")
        return dcc.Graph(figure=fig)
    except Exception as exc:
        logger.exception("Failed to create UMAP plot: %s", str(exc))
        return html.Div("An error occurred while creating the UMAP plot.")