from dash import html

def collapsible_sidebar():
    return html.Div(
        style={
            "backgroundColor": "#f8f9fa",
            "padding": "10px",
            "top": "10px",
            "left": "0px",
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
            html.H2("Menu", style={"textAlign": "center", "color": "#343a40"}),
            html.A("Upload Data", href="#upload-panel", style={"display": "block", "margin": "10px 0", "borderRadius": "3px", "padding": "5px", "backgroundColor": "#007bff", "color": "white", "textDecoration": "none"}),
            html.A("Quality Control", href="#qc-panel", style={"display": "block", "margin": "10px 0", "borderRadius": "3px", "padding": "5px", "backgroundColor": "#007bff", "color": "white", "textDecoration": "none"}),
            html.A("Preprocessing", href="#preprocess-panel", style={"display": "block", "margin": "10px 0", "borderRadius": "3px", "padding": "5px", "backgroundColor": "#007bff", "color": "white", "textDecoration": "none"}),
            html.A("Differential Expression", href="#differential-expression-panel", style={"display": "block", "margin": "10px 0", "borderRadius": "3px", "padding": "5px", "backgroundColor": "#007bff", "color": "white", "textDecoration": "none"}),
            html.Button("Option 5"),
            html.Button("Option 6"),
        ],
        hidden=True,
        id="sidebar"
    )

def toggle_sidebar():
    return html.Div(
        style={
            "top": "18px",
            "left": "0px",
            "zIndex": "1000",
            "position": "fixed",
        },
        children=[
            html.Button("Menu", id="toggle-button", n_clicks=0, style={"backgroundColor": "#007bff", "color": "white", "border": "none", "padding": "10px 20px", "borderRadius": "5px", "cursor": "pointer", "height": "40px"})
        ])