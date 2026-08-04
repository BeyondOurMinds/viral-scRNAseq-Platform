from dash import html, register_page

from viral_platform.layout.ViralBurden_panel import create_viral_burden_panel


register_page(__name__, path="/viral-burden", name="Viral Burden", order=6)


def layout():
    return html.Div(className="module-page", children=[create_viral_burden_panel()])
