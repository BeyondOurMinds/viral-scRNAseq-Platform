from dash import html, register_page

from viral_platform.layout.upload_panel import create_upload_panel


register_page(__name__, path="/upload", name="Upload Data", order=1)


def layout():
    return html.Div(className="module-page", children=[create_upload_panel()])
