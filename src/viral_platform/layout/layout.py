from dash import dcc, html

from viral_platform.layout.ViralBurden_panel import create_viral_burden_panel
from .header import create_header
from .sidebar import collapsible_sidebar, toggle_sidebar
from .upload_panel import create_upload_panel
from .QC_panel import create_qc_panel
from .PreprocessCluster_panel import create_preprocess_cluster_panel
from .DifferentialExpression_panel import create_differential_expression_panel
from .ViralGeneDetection_panel import create_viral_gene_detection_panel
from .ISG_panel import create_isg_panel
from .HostVirusInteraction_panel import create_host_virus_interaction_panel
from .CellCellCommunication_panel import create_CCC_panel
from .scMOVIR_reference_panel import create_scmovir_reference_panel
from .scMOVIRDownloadManager_panel import create_scmovir_download_manager_panel
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
                    label="Infection Analysis",
                    tab_id="IA-tab",
                    children=html.Div([
                        create_viral_gene_detection_panel(),
                        create_viral_burden_panel(),
                        create_isg_panel(),
                        create_host_virus_interaction_panel(),
                    ]),
                ),
                dbc.Tab(
                    label="Cell-Cell Communication",
                    tab_id="CCC-tab",
                    children=html.Div([
                        create_CCC_panel(),
                    ]),
                ),
                dbc.Tab(
                    label="scMOVIR Reference Database",
                    tab_id="SCMOVIR-tab",
                    children=html.Div([
                        create_scmovir_reference_panel(),
                        create_scmovir_download_manager_panel(),
                    ]),
                ),
            ]
        ),
    ]
    )