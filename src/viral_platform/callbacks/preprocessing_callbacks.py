from dash import Input, Output, no_update
from viral_platform.state.dataset_store import get_working_dataset
from viral_platform.analysis.preprocessing import preprocess_data
from viral_platform.plotting.elbow_plot import create_elbow_plot
import plotly.express as px
import plotly.graph_objects as go
import logging


logger = logging.getLogger(__name__)


def register_preprocessing_callbacks(app):
    @app.callback(
        Output("preprocess-loading-signal", "children"),
        Output("preprocess-temp-container", "children"),
        Input("run-preprocess-button", "n_clicks")
    )
    def run_preprocessing(n_clicks):
        if n_clicks is None:
            return no_update, no_update
        try:
            preprocess_data()
            adata = get_working_dataset()
            if adata is None:
                return "Preprocessing completed, but no dataset found.", no_update
            return "Preprocessing completed successfully.", create_elbow_plot(adata)
        except Exception as exc:
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