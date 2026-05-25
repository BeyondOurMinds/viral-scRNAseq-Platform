from dash import html
from .header import create_header
from .sidebar import collapsible_sidebar, toggle_sidebar
from .upload_panel import create_upload_panel

def create_layout():
    return html.Div(
        style={
            "overflowY": "scroll",
            "height": "400px",
            "padding": "10px",
        }, 
        children=[
        create_header(),
        toggle_sidebar(),
        collapsible_sidebar(),
        create_upload_panel(),
    ]
    )