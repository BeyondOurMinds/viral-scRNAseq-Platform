from dash import html, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_cached_result

def create_preprocess_cluster_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Preprocessing"),
            dbc.Row([
                dbc.Col(
                    dbc.Button("Run Preprocessing", id="run-preprocess-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced Options", id="advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                )
            ]),

            dcc.Loading(html.Div(id="preprocess-loading-signal", style={"display": "none"})),

            html.Div(id="preprocess-temp-container", children=get_cached_result("preprocess-temp-container", "Upload a dataset to run preprocessing.")),

            html.H2("Clustering"),
            dcc.Loading(html.Div(id="clustering-loading", style={"display": "none"})),
            html.Div(id="selected-pcs-output", style={"marginTop": "10px"}, children=get_cached_result("selected-pcs-output", "Select PCs to begin clustering analysis."))
        ], id="preprocess-panel"
    )
