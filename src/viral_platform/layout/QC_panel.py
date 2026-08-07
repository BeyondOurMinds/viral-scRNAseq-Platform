from dash import html, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_cached_result

def create_qc_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Quality Control"),
            dbc.Button("Generate QC Plots", id="generate-qc-plots-button", n_clicks=0, color="primary", className="mb-3"),
            dcc.Loading(html.Div(id="qc-generate-loading-signal", style={"display": "none"})),
            html.Div(id="qc-temp-container", children=get_cached_result("qc-temp-container", "Upload a dataset to view QC plots."))
        ],
        id="qc-panel"
    )
