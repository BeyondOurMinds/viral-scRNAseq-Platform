from dash import html

def create_header():
    """Persistent top toolbar rendered above all page content."""
    return html.Header(
        id="app-topbar",
        className="app-topbar",
        children=[
            html.Div(
                className="topbar-left",
                children=[
                    html.H1("SCJoseki", className="topbar-title"),
                    html.P(
                        "Single-Cell Analysis Platform",
                        className="topbar-subtitle",
                    ),
                ],
            ),
            html.Div(
                className="topbar-actions",
                children=[
                    html.Button(
                        "Collapse Sidebar",
                        id="sidebar-collapse-button",
                        className="topbar-button",
                        n_clicks=0,
                    ),
                    html.Button(
                        "Theme",
                        id="theme-toggle-button",
                        className="topbar-button",
                        n_clicks=0,
                    ),
                ],
            ),
        ],
    )