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
            "height": "calc(100vh - 70px)",
            "overflowY": "auto",
            "overflowX": "hidden",
            "boxSizing": "border-box",
        },
        children=[
            html.H2("Menu"),
            html.P("Fake button 1"),
            html.P("Fake button 2"),
            html.P("Fake button 3"),
            html.P("Fake button 4"),
            html.P("Fake button 5"),
            html.P("Fake button 6"),
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