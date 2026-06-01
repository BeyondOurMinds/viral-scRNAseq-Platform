from dash import html, dcc
import dash_bootstrap_components as dbc

def create_qc_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Quality Control"),
            html.P("This panel will contain QC metrics and visualizations for the uploaded dataset."),
            html.Div(id="qc-plot-container", children="Upload a dataset to view QC plots.")
        ],
        id="qc-panel"
    )