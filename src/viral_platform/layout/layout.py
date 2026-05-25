from dash import html
from .header import create_header

def create_layout():
    return html.Div([
        create_header(),
    ])