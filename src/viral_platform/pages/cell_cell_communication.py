from dash import html, register_page

from viral_platform.layout.CellCellCommunication_panel import create_CCC_panel


register_page(
    __name__,
    path="/cell-cell-communication",
    name="Cell-Cell Communication",
    order=11,
)


def layout():
    return html.Div(className="module-page", children=[create_CCC_panel()])
