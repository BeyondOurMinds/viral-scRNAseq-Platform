from dash import html, dcc
import dash_bootstrap_components as dbc

def create_cell_annotation_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Cell Annotation"),
            dbc.Row([
                dbc.Col(
                    dbc.Button("Run Cell Annotation", id="run-cell-annotation-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced Options", id="cell-annotation-advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                )
            ]),
            
            dcc.Loading(html.Div(id="cell-annotation-loading-signal", style={"display": "none"})),

            html.Div(id="cell-annotation-container", children="Upload a dataset to run cell annotation.")
        ], id="cell-annotation-panel"
    )