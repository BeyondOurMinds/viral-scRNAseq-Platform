from dash import html, dcc
from viral_platform.state.dataset_store import get_cached_result
import dash_bootstrap_components as dbc

def create_pathway_enrichment_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
             # title and run button
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            html.H4(
                                ["Pathway Enrichment Analysis"],
                                style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                            ),
                            html.P(
                                "Perform pathway enrichment analysis",
                                style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Button("Run Pathway Enrichment", id="run-pathway-enrichment-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced", id="pathway-enrichment-advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                ),
            ]),
        ],
    )