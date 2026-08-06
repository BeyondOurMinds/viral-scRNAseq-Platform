from dash import html, register_page

from viral_platform.layout.ISG_panel import create_isg_panel


register_page(__name__, path="/isg-analysis", name="ISG Analysis", order=9)


def layout():
    return html.Div(className="module-page", children=[create_isg_panel()])
