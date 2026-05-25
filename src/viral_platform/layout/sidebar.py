from dash import html

def collapsible_sidebar():
    return html.Div(
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "10px",
            "margin": "10px",
            "borderRadius": "5px",
            "width": "250px",
            "position": "fixed",
            "zIndex": "999",
            "height": "calc(100vh - 70px)",
            "overflowY": "auto",
            "overflowX": "hidden",
            "boxSizing": "border-box",
        },
        children=[
            html.H2("Menu"),
            html.A("Upload Data", href="#upload-panel", style={"display": "block", "margin": "10px 0", "borderRadius": "3px", "padding": "5px", "backgroundColor": "#007bff", "color": "white", "textDecoration": "none"}),
            html.Button("Option 2"),
            html.Button("Option 3"),
            html.Button("Option 4"),
            html.Button("Option 5"),
            html.Button("Option 6"),
        ],
        hidden=True,
        id="sidebar"
    )

def toggle_sidebar():
    return html.Div(
        style={
            "top": "10px",
            "left": "10px",
            "zIndex": "1000",
        },
        children=[
            html.Button("Menu", id="toggle-button", n_clicks=0)
        ])