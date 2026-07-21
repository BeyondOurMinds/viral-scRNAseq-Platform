from dash import html

def create_header():
    return html.Div(
        style={
            "backgroundColor": "#333",
            "color": "white",
            "padding": "10px",
            "textAlign": "center",
        },
        children=[
            html.H1("SCJoseki", style={"margin": "0", "fontWeight": "bold", "color": "#ffffff", "fontFamily": "Arial, sans-serif", "letterSpacing": "1px"}),
            html.P("A platform for analyzing viral single-cell RNA sequencing data", style={"margin": "0"}),
        ],
    )