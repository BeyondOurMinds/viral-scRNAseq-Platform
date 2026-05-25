from dash import html

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
            html.P("This is where users can upload their viral scRNA-seq data."),
        ],
        id="upload-panel"
    )