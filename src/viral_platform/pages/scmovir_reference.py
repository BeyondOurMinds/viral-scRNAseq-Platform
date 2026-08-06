from dash import html, register_page

from viral_platform.layout.scMOVIR_reference_panel import create_scmovir_reference_panel
from viral_platform.layout.scMOVIRDownloadManager_panel import (
    create_scmovir_download_manager_panel,
)


register_page(__name__, path="/scmovir-reference", name="scMOVIR Reference", order=12)


def layout():
    return html.Div(
        className="module-page",
        children=[
            create_scmovir_reference_panel(),
            create_scmovir_download_manager_panel(),
        ],
    )
