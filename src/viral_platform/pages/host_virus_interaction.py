from dash import html, register_page

from viral_platform.layout.HostVirusInteraction_panel import create_host_virus_interaction_panel


register_page(
    __name__,
    path="/host-virus-interaction",
    name="Host-Virus Interaction",
    order=8,
)


def layout():
    return html.Div(className="module-page", children=[create_host_virus_interaction_panel()])
