from dash import html, dcc
import dash_bootstrap_components as dbc

def create_differential_expression_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Differential Expression Analysis"),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id="grouping-variable-dropdown",
                        options=[
                            {"label": "Upload a dataset to select grouping variable", "value": ""},
                        ],
                        placeholder="Select Grouping Variable",
                        searchable=True,
                    )
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="group1-dropdown",
                        options=[
                            {"label": "Select a grouping variable to select group 1", "value": ""},
                        ],
                        placeholder="Select Group 1",
                        searchable=True,
                    )
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="group2-dropdown",
                        options=[
                            {"label": "Select a grouping variable to select group 2", "value": ""},
                        ],
                        placeholder="Select Group 2",
                        searchable=True,
                    )
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="celltype-dropdown",
                        options=[
                            {"label": "Upload a dataset to select cell type", "value": ""},
                        ],
                        placeholder="Select Cell Type",
                        searchable=True,
                    )
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    dbc.Button("Run Differential Expression Analysis", id="run-differential-expression-analysis-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced Options", id="differential-expression-advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                )
            ], style={"marginTop": "8px"}),
            dbc.Row([
                dbc.Col(
                    dcc.Loading(html.Div(id="differential-expression-loading-signal", style={"display": "none"})),
                    width="auto"
                )
            ]),
            html.Div(id="differential-expression-temp-container", children="Upload a dataset to run differential expression analysis.")
        ], id="differential-expression-panel"
    )