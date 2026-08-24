from dash import html, register_page
from viral_platform.layout.PathwayEnrichment_panel import create_pathway_enrichment_panel

register_page(
    __name__,
    path="/pathway-enrichment",
    name="Pathway Enrichment",
    order=6,
)

def layout():
    return html.Div(className="module-page", children=[create_pathway_enrichment_panel()])