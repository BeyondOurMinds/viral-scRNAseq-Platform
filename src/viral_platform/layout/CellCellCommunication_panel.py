from dash import html, dcc
import dash_bootstrap_components as dbc


def create_CCC_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            # title and run button
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(
                                    ["1. Cell-Cell Communication Analysis"],
                                    style={
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "marginBottom": "2px",
                                    },
                                ),
                                html.P(
                                    "Identify cell-cell communication interactions",
                                    style={
                                        "color": "#6c757d",
                                        "marginBottom": "16px",
                                        "fontSize": "14px",
                                    },
                                ),
                            ]
                        ),
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Run Cell-Cell Communication",
                            id="run-ccc-button",
                            n_clicks=0,
                            color="primary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                ]
            ),
            # parameter selection
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="ccc-grouping-dropdown",
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
                            id="ccc-method-dropdown",
                            options=[
                                {"label": "Rank Aggregate", "value": "rank_aggregate"},
                            ],
                            value="rank_aggregate",
                            searchable=True,
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="ccc-resource-dropdown",
                            options=[
                                {"label": "Consensus", "value": "consensus"},
                            ],
                            value="consensus",
                            searchable=True,
                        )
                    ),
                ]
            ),
            # loading signal
            dcc.Loading(
                type="default",
                children=html.Div(id="ccc-loading-signal", style={"display": "none"}),
            ),
            # summary table
            # output tabs
            dbc.Tabs(
                id="ccc-output-tabs",
                active_tab="ccc-summary-tab",
                children=[
                    dbc.Tab(
                        label="Summary Table",
                        tab_id="ccc-summary-tab",
                        children=html.Div(
                            id="ccc-summary-container",
                            children=[
                                html.P(
                                    "No cell-cell communication results yet. Run the analysis to see results here.",
                                    style={
                                        "color": "#6c757d",
                                        "fontSize": "14px",
                                        "marginTop": "10px",
                                    },
                                )
                            ],
                        ),
                    ),
                    dbc.Tab(
                        label="Bubble Plot",
                        tab_id="ccc-bubble-tab",
                        children=html.Div(
                            id="ccc-bubble-container",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                id="ccc-bubble-plot-container",
                                                children=[
                                                    html.P(
                                                        "No cell-cell communication results yet. Run the analysis to see results here.",
                                                        style={
                                                            "color": "#6c757d",
                                                            "fontSize": "14px",
                                                            "marginTop": "10px",
                                                        },
                                                    )
                                                ],
                                            ),
                                        )
                                    ]
                                ),
                            ],
                        ),
                    ),
                    dbc.Tab(
                        label="Network Plot",
                        tab_id="ccc-network-tab",
                        children=html.Div(
                            id="ccc-network-container",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                id="ccc-network-plot-container",
                                                children=[
                                                    html.P(
                                                        "No cell-cell communication results yet. Run the analysis to see results here.",
                                                        style={
                                                            "color": "#6c757d",
                                                            "fontSize": "14px",
                                                            "marginTop": "10px",
                                                        },
                                                    )
                                                ],
                                            ),
                                        )
                                    ]
                                ),
                            ],
                        ),
                    ),
                    dbc.Tab(
                        label="Reference",
                        tab_id="ccc-reference-tab",
                        children=html.Div(
                            id="ccc-reference-container",
                            style={"padding": "15px"},
                            children=[
                                html.P(
                                    "Select a downloaded CellPhoneDB reference file."
                                ),
                                dcc.RadioItems(
                                    id="ccc-reference-file-radio",
                                    options=[
                                        {
                                            "label": "No downloaded CellPhoneDB files found.",
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
                                    "Select",
                                    id="ccc-reference-select-button",
                                    n_clicks=0,
                                    color="secondary",
                                    className="mt-2",
                                ),
                                html.Hr(),
                                html.Div(
                                    id="ccc-reference-results-container",
                                    children="Reference CCC outputs will appear here.",
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            # Filter Selection
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="ccc-source-filter-dropdown",
                            options=[
                                {"label": "All Sources", "value": "_all_"},
                            ],
                            placeholder="Filter by Source Cell Type",
                        )
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="ccc-target-filter-dropdown",
                            options=[
                                {"label": "All Targets", "value": "_all_"},
                            ],
                            placeholder="Filter by Target Cell Type",
                        )
                    ),
                    dbc.Col(
                        dcc.Input(
                            id="ccc-interaction-filter-input",
                            type="number",
                            placeholder="Show top interactions",
                            min=1,
                            max=5000,
                            step=1,
                        )
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Apply Filters",
                            id="ccc-apply-filters-button",
                            n_clicks=0,
                            color="primary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Reset Filters",
                            id="ccc-reset-filters-button",
                            n_clicks=0,
                            color="secondary",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Checklist(
                            id="ccc-show-network-labels",
                            options=[{"label": "Show Network labels?", "value": True}],
                            value=[True],
                            inline=True,
                            inputStyle={"marginRight": "6px"},
                            labelStyle={"display": "flex", "alignItems": "center"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Export Network Fullscreen HTML",
                            id="ccc-export-network-html-button",
                            n_clicks=0,
                            color="info",
                            className="mb-3",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dcc.Loading(
                            id="ccc-export-loading-indicator",
                            type="default",
                            children=html.Div(
                                id="ccc-export-loading-signal",
                                style={
                                    "minWidth": "200px",
                                    "fontSize": "12px",
                                    "color": "#6c757d",
                                    "paddingTop": "8px",
                                },
                            ),
                        ),
                        width="auto",
                    ),
                ]
            ),
            dcc.Download(id="ccc-network-html-download"),
        ],
    )
