from dash import Input, Output, State, no_update
from viral_platform.state.dataset_store import cache_results, get_working_dataset
from viral_platform.analysis.preprocessing import preprocess_data, run_clustering
from viral_platform.plotting.elbow_plot import create_elbow_plot
from viral_platform.plotting.clustering import create_umap_plot
import plotly.express as px
import plotly.graph_objects as go
import logging


logger = logging.getLogger(__name__)


def register_preprocessing_callbacks(app):
    @app.callback(
        Output("preprocess-loading-signal", "children"),
        Output("preprocess-temp-container", "children"),
        Input("run-preprocess-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def run_preprocessing(n_clicks):
        if not n_clicks:
            return no_update, no_update
        try:
            preprocess_data()
            adata = get_working_dataset()
            if adata is None:
                logger.warning("Preprocessing completed but no dataset found in state store.")
                return "Preprocessing completed, but no dataset found.", no_update
            logger.info("Preprocessing completed successfully.")
            result = create_elbow_plot(adata)
            cache_results(**{"preprocess-temp-container": result})
            return "Preprocessing completed successfully.", result
        except Exception as exc:
            logger.exception("Preprocessing failed: %s", str(exc))
            return f"Preprocessing failed: {str(exc)}", no_update
        
    @app.callback(
        Output("elbow-plot", "figure"),
        Input("pc-slider", "value")
    )
    def update_elbow_plot(n_pcs):
        adata = get_working_dataset()
        if adata is None:
            return px.bar(title="Elbow Plot")
        try:
            elbow_layout = create_elbow_plot(adata)
            elbow_fig = go.Figure(elbow_layout.children[0].figure)
            if n_pcs is not None:
                elbow_fig.add_vline(
                    x=n_pcs,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Selected PCs: {n_pcs}",
                    annotation_position="top right",
                )
            return elbow_fig
        except Exception as exc:
            logger.exception("Failed to update elbow plot: %s", str(exc))
            return px.bar(title="Elbow Plot")
    
    @app.callback(
        Output("clustering-loading", "children"),
        Output("selected-pcs-output", "children"),
        Input("select-pcs-button", "n_clicks"),
        State("pc-slider", "value"),
        prevent_initial_call=True,
    )
    def apply_pca_selection(n_clicks, n_pcs):
        if not n_clicks or n_pcs is None:
            return no_update, no_update
        try:
            logger.info("Apply PCA selection clicked. n_clicks=%s, n_pcs=%s", n_clicks, n_pcs)
            run_clustering(n_dims=n_pcs)
            logger.info("PCA selection applied successfully with %d PCs.", n_pcs)
            return f"PCA selection applied with {n_pcs} PCs.", create_umap_plot()
        except Exception as exc:
            logger.exception("Failed to apply PCA selection: %s", str(exc))
            return f"Failed to apply PCA selection: {str(exc)}", no_update
