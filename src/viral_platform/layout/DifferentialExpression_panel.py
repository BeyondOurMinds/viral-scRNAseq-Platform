from dash import html, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_cached_result


def create_differential_expression_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Differential Expression Analysis"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="grouping-variable-dropdown",
                            options=[
                                {
                                    "label": "Upload a dataset to select grouping variable",
                                    "value": "",
                                },
                            ],
                            placeholder="Select Grouping Variable",
                            searchable=True,
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="group1-dropdown",
                            options=[
                                {
                                    "label": "Select a grouping variable to select group 1",
                                    "value": "",
                                },
                            ],
                            placeholder="Select Group 1",
                            searchable=True,
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="group2-dropdown",
                            options=[
                                {
                                    "label": "Select a grouping variable to select group 2",
                                    "value": "",
                                },
                            ],
                            placeholder="Select Group 2",
                            searchable=True,
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="celltype-variable-dropdown",
                            options=[
                                {
                                    "label": "Upload a dataset to select cell type column",
                                    "value": "",
                                },
                            ],
                            placeholder="Select Cell Type Column",
                            searchable=True,
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="celltype-dropdown",
                            options=[
                                {
                                    "label": "Select a cell type column to load cell types",
                                    "value": "",
                                },
                            ],
                            placeholder="Select Cell Type",
                            searchable=True,
                        )
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Run Differential Expression Analysis",
                            id="run-differential-expression-analysis-button",
                            n_clicks=0,
                            color="primary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Advanced Options",
                            id="differential-expression-advanced-options-button",
                            n_clicks=0,
                            color="secondary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                ],
                style={"marginTop": "8px"},
            ),
            dbc.Collapse(
                id="differential-expression-advanced-options-collapse",
                is_open=False,
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P("Minimum cells per pseudobulk sample"),
                                    dcc.Slider(
                                        id="de-min-psbulk-cells-slider",
                                        min=1,
                                        max=100,
                                        step=1,
                                        value=10,
                                        marks={1: "1", 10: "10", 50: "50", 100: "100"},
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.P("Minimum counts per pseudobulk sample"),
                                    dcc.Slider(
                                        id="de-min-psbulk-counts-slider",
                                        min=100,
                                        max=10000,
                                        step=100,
                                        value=1000,
                                        marks={100: "100", 1000: "1k", 5000: "5k", 10000: "10k"},
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.P("Minimum gene count"),
                                    dcc.Slider(
                                        id="de-min-gene-count-slider",
                                        min=1,
                                        max=50,
                                        step=1,
                                        value=10,
                                        marks={1: "1", 10: "10", 25: "25", 50: "50"},
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col(
                                [
                                    html.P("Minimum samples per gene"),
                                    dcc.Slider(
                                        id="de-min-samples-per-gene-slider",
                                        min=1,
                                        max=10,
                                        step=1,
                                        value=2,
                                        marks={1: "1", 2: "2", 5: "5", 10: "10"},
                                    ),
                                ],
                                md=3,
                            ),
                        ],
                        style={"marginBottom": "12px"},
                    ),
                    dbc.Button(
                        "Reset Advanced Defaults",
                        id="de-advanced-reset-button",
                        n_clicks=0,
                        color="secondary",
                        outline=True,
                        className="mb-3",
                    ),
                ],
            ),
            
            dcc.Loading(
                html.Div(
                    id="differential-expression-loading-signal",
                    style={"display": "none"},
                )
            ),
            
            dbc.Tabs(
                id="differential-expression-output-tabs",
                active_tab="pseudobulk-tab",
                children=[
                    dbc.Tab(
                        label="Pseudobulk",
                        tab_id="pseudobulk-tab",
                        children=html.Div(
                            id="pseudobulk-container",
                            children=get_cached_result("pseudobulk-container", "Upload a dataset to run differential expression analysis."),
                            style={"padding": "15px"},
                        ),
                    ),
                    dbc.Tab(
                        label="DE Table",
                        tab_id="de-table-tab",
                        children=html.Div(
                            id="de-table-container",
                            children=get_cached_result("de-table-container", "DE table output will appear here."),
                            style={"padding": "15px"},
                        ),
                    ),
                    dbc.Tab(
                        label="Volcano Plot",
                        tab_id="volcano-plot-tab",
                        children=html.Div(
                            id="volcano-plot-container",
                            children=get_cached_result("volcano-plot-container", "Volcano plot output will appear here."),
                            style={"padding": "15px"},
                        ),
                    ),
                    dbc.Tab(
                        label="Heatmap",
                        tab_id="de-heatmap-tab",
                        children=html.Div(
                            id="de-heatmap-container",
                            children=get_cached_result("de-heatmap-container", "Heatmap output will appear here."),
                            style={"padding": "15px"},
                        ),
                    ),
                    dbc.Tab(
                        label="Reference",
                        tab_id="de-reference-tab",
                        children=html.Div(
                            id="de-reference-container",
                            style={"padding": "15px"},
                            children=[
                                html.P("Select a downloaded DE reference file."),
                                dcc.RadioItems(
                                    id="de-reference-file-radio",
                                    options=[
                                        {
                                            "label": "No downloaded DE reference files found.",
                                            "value": "",
                                        },
                                    ],
                                    value="",
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "6px",
                                    },
                                ),
                                dbc.Button(
                                    "Display Reference",
                                    id="de-reference-display-button",
                                    n_clicks=0,
                                    color="secondary",
                                    className="mt-2",
                                ),
                                html.Hr(),
                                html.Div(
                                    id="de-reference-results-container",
                                    children=get_cached_result("de-reference-results-container", "Reference DE outputs will appear here."),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
        id="differential-expression-panel",
    )
