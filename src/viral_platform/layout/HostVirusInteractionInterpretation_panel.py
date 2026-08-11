from dash import html, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_cached_result
import dash_cytoscape as cyto


def create_host_virus_interaction_interpretation_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            # title and run button
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            html.H4(
                                ["4.1 Host-Virus Interaction Interpretation"],
                                style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                            ),
                            html.P(
                                "Interpret Host Genes with curated Virus-Host Interaction Databases",
                                style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Button("Run Host-Virus Interaction Interpretation", id="run-host-virus-interaction-interpretation-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                )
            ]),

            # dropdowns for virus and gene source selection
            dbc.Row([
                dbc.Col(
                    children=[
                        html.P("Select Virus"),
                        dcc.Dropdown(
                            id="host-virus-interaction-interpretation-dropdown",
                            options=[],
                        )
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Row([
                            html.P("Gene Source"),
                            dcc.Dropdown(
                                id="host-virus-interaction-gene-source-dropdown",
                                options=[
                                    {"label": "Differentially Expressed Genes", "value": "deg"},
                                    {"label": "Interferon-Stimulated Genes", "value": "isg"},
                                    {"label": "Host-Virus Interaction Genes", "value": "hvi"},
                                    {"label": "Custom Gene List", "value": "custom"},
                                ],
                            )
                        ]),
                        # hidden dropdown for cell type selection (only shown when gene source is DEG)
                        dbc.Row([
                            html.Div(
                                id="hvi-interpretation-celltype-dropdown-container",
                                children=[
                                    html.P("Cell type"),
                                    dcc.Dropdown(
                                        id="hvi-interpretation-celltype-dropdown",
                                        options=[]
                                    ),
                                ],
                                style={"marginTop": "10px"},
                                hidden=True,
                            ),
                        ]),
                        # hidden text area for custom gene list (only shown when gene source is custom)
                        dbc.Row([
                            html.Div(
                                id="custom-hvi-gene-list-container",
                                children=[
                                    html.P("Custom List"),
                                    dbc.Textarea(
                                        id="custom-hvi-gene-list-input",
                                        placeholder="Enter custom gene list (comma-separated)",
                                        wrap=True,
                                    )
                                ],
                                style={"marginTop": "10px"},
                                hidden=True,
                            ),
                        ]),
                    ],
                ),
                
            ]),

            # loading signal
            dcc.Loading(
                type="default",
                children=html.Div(id="host-virus-interaction-interpretation-loading-signal", style={"display": "none"}),
            ),

            # results container
            dbc.Tabs(
                id="host-virus-interaction-interpretation-output-tabs",
                active_tab="summary-tab",
                children=[
                    dbc.Tab(
                        label="Summary Table",
                        tab_id="summary-tab",
                        children=html.Div(
                                    id="host-virus-interaction-interpretation-results-container",
                                    children=get_cached_result("host-virus-interaction-interpretation-results-container", [
                                        html.P(
                                            "No host-virus interaction interpretation results yet. Run the analysis to see results here.",
                                            style={"color": "#6c757d", "fontSize": "14px", "marginTop": "10px"},
                                        )
                                    ]),
                                ),
                    ),
                    dbc.Tab(
                        label="Cytoscape Network",
                        tab_id="cytoscape-network-tab",
                        children=html.Div(
                            id="cytoscape-network-container",
                            children=[
                                cyto.Cytoscape(
                                    id="host-virus-interaction-network",
                                    elements=get_cached_result("host-virus-interaction-network", []),
                                    layout={
                                        "name": "preset",
                                        "fit": True,
                                        "padding": 30,
                                    },
                                    minZoom=0.5,
                                    maxZoom=2,
                                    style={
                                        "width": "100%",
                                        "height": "700px",
                                    },
                                    stylesheet=[
                                        {
                                            "selector": 'node[node_type="virus"]',
                                            "style": {
                                                "background-color": "#d62728",
                                                "label": "data(label)",
                                                "color": "#000000",
                                                "text-valign": "center",
                                                "text-halign": "center",
                                                "width": 40,
                                                "height": 40,
                                            },
                                        },
                                        {
                                            "selector": 'node[node_type="host"]',
                                            "style": {
                                                "background-color": "#1f77b4",
                                                "label": "data(label)",
                                                "color": "#000000",
                                                "text-valign": "center",
                                                "text-halign": "center",
                                                "width": 35,
                                                "height": 35,
                                            },
                                        },
                                        {
                                            "selector": "edge",
                                            "style": {
                                                "curve-style": "bezier",
                                                "target-arrow-shape": "triangle",
                                                "arrow-scale": 1,
                                                "line-color": "#888888",
                                                "target-arrow-color": "#888888",
                                            },
                                        },
                                    ],
                                )
                            ],
                        ),
                    ),
                ],
            ),
            
        ],
    )


