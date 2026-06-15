from dash import html, dcc
import dash_bootstrap_components as dbc

def create_infection_analysis_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Infection Analysis"),
            dbc.Row([
                dbc.Col(
                    dbc.Button("Run Infection Analysis", id="run-infection-analysis-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Advanced Options", id="infection-advanced-options-button", n_clicks=0, color="secondary", className="mb-3"),
                    width="auto"
                )
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Loading(html.Div(id="infection-analysis-loading-signal", style={"display": "none"})),
                    width="auto"
                )
            ]),
            html.Div(id="infection-analysis-temp-container", children="Upload a dataset to run infection analysis.")
        ], id="infection-analysis-panel"
    )