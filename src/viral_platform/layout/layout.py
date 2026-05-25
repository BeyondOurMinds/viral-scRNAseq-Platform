from dash import html
from .header import create_header
from .sidebar import create_sidebar

def create_layout():
    return html.Div(
        style={
            "overflowY": "scroll",
            "height": "400px",
            "padding": "10px",
        }, 
        children=[
        create_header(),
        create_sidebar(),
    ]
    )