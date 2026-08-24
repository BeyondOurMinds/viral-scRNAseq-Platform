from dash import html, register_page

from viral_platform.layout.HostVirusInteraction_panel import create_host_virus_interaction_panel
from viral_platform.layout.HostVirusInteractionInterpretation_panel import create_host_virus_interaction_interpretation_panel


register_page(
    __name__,
    path="/host-virus-interaction",
    name="Host-Virus Interaction",
    order=10,
)


def layout():
    return html.Div(className="module-page", children=[
        create_host_virus_interaction_panel(),
        create_host_virus_interaction_interpretation_panel(),
    ])
