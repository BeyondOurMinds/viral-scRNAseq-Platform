from dash import html, register_page

from viral_platform.layout.PreprocessCluster_panel import create_preprocess_cluster_panel


register_page(__name__, path="/preprocessing", name="Preprocessing", order=3)


def layout():
    return html.Div(className="module-page", children=[create_preprocess_cluster_panel()])
