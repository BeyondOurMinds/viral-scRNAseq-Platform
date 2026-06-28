from dash import html, dcc
import dash_bootstrap_components as dbc

def create_viral_burden_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Viral Burden Analysis"),
        ]
    )