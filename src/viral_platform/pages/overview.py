from dash import html, register_page

from viral_platform.layout.Overview_panel import create_overview_panel


register_page(__name__, path="/", name="Overview", order=0)


def layout():
    """Landing page shown at the root route."""
    return html.Div(
        className="module-page",
        children=[
            create_overview_panel(),
        ],
    )
