from dash import html


_SCJOSEKI_LOGO = "/assets/SCJosekiLogoTransparent.png"
_CVR_LOGO = "/assets/CVR.jpg"

def create_header():
    """Persistent top toolbar rendered above all page content."""
    return html.Header(
        id="app-topbar",
        className="app-topbar",
        children=[
            html.Div(
                className="topbar-left",
                children=[
                    html.Img(
                        src=_SCJOSEKI_LOGO,
                        className="topbar-logo",
                        alt="SCJoseki logo",
                        style={"width": "52px", "height": "52px", "objectFit": "contain", "flex": "0 0 auto"},
                    ),
                    html.Div(
                        className="topbar-title-group",
                        children=[
                            html.H1("SCJoseki", className="topbar-title"),
                            html.P(
                                "Single-Cell Analysis Platform",
                                className="topbar-subtitle",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="topbar-right",
                children=[
                    html.Img(
                        src=_CVR_LOGO,
                        className="topbar-cvr-logo",
                        alt="Center for Virus Research logo",
                        style={"width": "76px", "height": "56px", "objectFit": "contain", "flex": "0 0 auto"},
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
            ),
        ],
    )