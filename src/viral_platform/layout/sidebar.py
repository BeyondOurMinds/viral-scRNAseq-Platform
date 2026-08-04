from dash import dcc, html

from viral_platform.layout.navigation import NAV_ITEMS


def path_to_token(path):
    """Convert a route path into a stable token suitable for component IDs."""
    if path == "/":
        return "root"
    return path.strip("/").replace("/", "-")


def _build_sidebar_link(item):
    """Render one sidebar link with predictable IDs for active/collapse callbacks."""
    path = item["path"]
    token = path_to_token(path)
    return dcc.Link(
        href=path,
        className="sidebar-link",
        id=f"sidebar-link-{token}",
        children=[
            html.Span(item["icon"], className="sidebar-link-icon"),
            html.Span(
                item["label"],
                className="sidebar-link-label",
                id=f"sidebar-link-label-{token}",
            ),
        ],
    )


def create_sidebar():
    """Permanent left navigation sidebar for Dash Pages routing."""
    return html.Aside(
        id="app-sidebar",
        className="app-sidebar",
        children=[
            html.Div(
                className="sidebar-brand",
                children=[
                    html.H2("SCJoseki", className="sidebar-brand-title"),
                    html.P("Single-Cell Analysis Platform", className="sidebar-brand-subtitle"),
                ],
            ),
            html.Nav(className="sidebar-nav", children=[_build_sidebar_link(item) for item in NAV_ITEMS]),
            html.Div(
                className="sidebar-footer",
                children=[
                    html.P("Current Dataset", className="sidebar-footer-title"),
                    html.P("No dataset loaded", id="sidebar-dataset-status", className="sidebar-footer-status"),
                ],
            ),
        ],
    )