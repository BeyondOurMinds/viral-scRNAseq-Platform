from dash import html, register_page

from viral_platform.layout.QC_panel import create_qc_panel


register_page(__name__, path="/qc", name="QC and Filtering", order=2)


def layout():
    return html.Div(className="module-page", children=[create_qc_panel()])
