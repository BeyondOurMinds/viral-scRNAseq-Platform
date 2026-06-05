from dash import Input, Output, State, html, no_update
from viral_platform.state.dataset_store import get_working_dataset
from viral_platform.analysis.preprocessing import preprocess_data
from viral_platform.plotting.elbow_plot import create_elbow_plot

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