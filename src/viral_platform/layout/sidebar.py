from dash import html

def create_sidebar():
    return html.Div(
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "10px",
            "width": "250px",
            "float": "left",
        },
        children=[
            html.H2("Sidebar"),
            html.P("This is the sidebar content."),
        ],
    )