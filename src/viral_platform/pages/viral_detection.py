from dash import html, register_page

from viral_platform.layout.ViralGeneDetection_panel import create_viral_gene_detection_panel


register_page(__name__, path="/viral-detection", name="Viral Detection", order=5)


def layout():
    return html.Div(className="module-page", children=[create_viral_gene_detection_panel()])
