from dash import dcc, html
from .header import create_header
from .sidebar import collapsible_sidebar, toggle_sidebar
from .upload_panel import create_upload_panel
from .QC_panel import create_qc_panel

def create_layout():
    return html.Div(
        style={
            "overflowY": "scroll",
            "height": "400px",
            "padding": "10px",
        }, 
        children=[
        dcc.Store(id="active-dataset-version", data=None, storage_type="session"),
        create_header(),
        toggle_sidebar(),
        collapsible_sidebar(),
        create_upload_panel(),
        create_qc_panel(),
    ]
    )