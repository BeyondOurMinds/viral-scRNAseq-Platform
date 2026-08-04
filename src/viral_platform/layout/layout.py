from dash import dcc, html, page_container

from .header import create_header
from .sidebar import create_sidebar

def create_layout():
    """Build the app shell and shared stores used by all Dash pages."""
    return html.Div(
        id="app-shell",
        className="app-shell",
        children=[
            dcc.Store(id="active-dataset-version", data=None, storage_type="memory"),
            dcc.Store(id="ui-theme-mode", data="light", storage_type="local"),
            # Location is used for active-link styling and page routing state.
            dcc.Location(id="app-location", refresh=False),
            create_sidebar(),
            html.Div(
                id="app-content-shell",
                className="app-content-shell",
                children=[
                    create_header(),
                    html.Main(id="app-page-content", className="app-page-content", children=[page_container]),
                ],
            ),
        ],
    )