from dash import html, dcc
from viral_platform.state.dataset_store import get_cached_result
import dash_bootstrap_components as dbc

def create_cell_annotation_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
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
                                ["Cell Annotation"],
                                style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                            ),
                            html.P(
                                "Annotate cell types using celltypist",
                                style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Button("Run Cell Annotation", id="run-cell-annotation-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced", id="cell-annotation-advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                ),
            ]),

            # loading signal
            dcc.Loading(
                type="default",
                children=html.Div(id="cell-annotation-loading-signal", style={"display": "none"}),
            ),

            # results container
            html.Div(id="cell-annotation-results-container", children=get_cached_result("cell-annotation-results-container", ["No cell annotation results yet. Run the analysis to see results here."])),
        ], id="cell-annotation-panel"
    )
