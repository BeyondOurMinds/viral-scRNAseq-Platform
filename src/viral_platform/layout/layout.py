from dash import dcc, html
from .header import create_header
from .sidebar import collapsible_sidebar, toggle_sidebar
from .upload_panel import create_upload_panel
from .QC_panel import create_qc_panel
from .PreprocessCluster_panel import create_preprocess_cluster_panel
from .InfectionAnalysis_panel import create_infection_analysis_panel

def create_layout():
    return html.Div(
        style={
            "overflowY": "scroll",
            "height": "100vh",
            "padding": "10px",
        }, 
        children=[
        dcc.Store(id="active-dataset-version", data=None, storage_type="session"),
        create_header(),
        toggle_sidebar(),
        collapsible_sidebar(),
        create_upload_panel(),
        create_qc_panel(),
        create_preprocess_cluster_panel(),
        create_infection_analysis_panel(),
    ]
    )