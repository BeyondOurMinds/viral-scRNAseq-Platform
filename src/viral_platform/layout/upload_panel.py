from dash import html, Dash, dcc
import dash_bootstrap_components as dbc

def create_upload_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "margin": "10px",
            "borderRadius": "5px",
        },
        children=[
            html.H2("Upload Panel"),
            html.Button("Upload File", id="upload-button", style={"align": "center"}),
            dcc.Input(type="text", id="file-input", value="Please Select a File", readOnly=True),
        ],
        id="upload-panel"
    )