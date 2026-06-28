from dash import dcc, html

from viral_platform.layout.ViralBurden_panel import create_viral_burden_panel
from .header import create_header
from .sidebar import collapsible_sidebar, toggle_sidebar
from .upload_panel import create_upload_panel
from .QC_panel import create_qc_panel
from .PreprocessCluster_panel import create_preprocess_cluster_panel
from .DifferentialExpression_panel import create_differential_expression_panel
import dash_bootstrap_components as dbc

def create_layout():
    return html.Div(
        style={
            "overflowY": "scroll",
            "height": "100vh",
            "padding": "10px",
        }, 
        children=[
        dcc.Store(id="active-dataset-version", data=None, storage_type="memory"),
        dcc.Location(id="page-location", refresh=False),
        create_header(),
        toggle_sidebar(),
        collapsible_sidebar(),
        create_upload_panel(),
        dbc.Tabs(
            id="layout-tabs",
            active_tab="QC-tab",
            children=[
                dbc.Tab(
                    label="Quality Control",
                    tab_id="QC-tab",
                    children=html.Div([
                        create_qc_panel(),
                        create_preprocess_cluster_panel()
                    ]),
                ),
                dbc.Tab(
                    label="Differential Expression",
                    tab_id="DE-tab",
                    children=html.Div([
                        create_differential_expression_panel()
                    ]),
                ),
                dbc.Tab(
                    label="Viral Burden",
                    tab_id="VB-tab",
                    children=html.Div([
                        create_viral_burden_panel()
                    ]),
                ),
            ]
        ),
    ]
    )