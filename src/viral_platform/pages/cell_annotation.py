from dash import html, register_page
from viral_platform.layout.CellAnnotation_panel import create_cell_annotation_panel

register_page(
    __name__,
    path="/cell-annotation",
    name="Cell Annotation",
    order=4,
)

def layout():
    return html.Div(className="module-page", children=[create_cell_annotation_panel()])