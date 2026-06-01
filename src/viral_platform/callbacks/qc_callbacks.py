from dash import Input, Output, html

from viral_platform.plotting.QC_plots import create_qc_plots
from viral_platform.state.dataset_store import get_dataset


def register_qc_callbacks(app):
    @app.callback(Output("qc-plot-container", "children"), Input("active-dataset-version", "data"))
    def render_qc_plots(_dataset_version):
        adata = get_dataset()
        if adata is None:
            return "Upload a dataset to view QC plots."

        return create_qc_plots(adata)