from dash import html, dcc
import dash_bootstrap_components as dbc


_PANEL_STYLE = {
    "backgroundColor": "#eff7ff",
    "padding": "20px",
    "borderRadius": "5px",
    "border": "1px solid #000000",
    "margin": "0 0 20px 0",
}


def create_scmovir_reference_panel():
    return html.Div(
        children=[
            dcc.Store(id="scmovir-active-filters", data=None),
            

            html.Div(
                style=_PANEL_STYLE,
                children=[
                    # title
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H4(
                                            ["1. SCMOVIR Reference Database"],
                                            style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                                        ),
                                        html.P(
                                            "Search the SCMOVIR reference database",
                                            style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                                        ),
                                    ]
                                ),
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Find Reference(s)",
                                    id="find-scmovir-reference-button",
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
                                children=[
                                    html.P("Select Virus"),
                                    dcc.Dropdown(
                                        id="scmovir-virus-dropdown",
                                        options=[],
                                        placeholder="Select Virus",
                                        searchable=True,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.P("Select Disease"),
                                    dcc.Dropdown(
                                        id="scmovir-disease-dropdown",
                                        options=[],
                                        placeholder="Select Disease",
                                        searchable=True,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.P("Select Tissue"),
                                    dcc.Dropdown(
                                        id="scmovir-tissue-dropdown",
                                        options=[],
                                        placeholder="Select Tissue",
                                        searchable=True,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.P("Select Platform"),
                                    dcc.Dropdown(
                                        id="scmovir-platform-dropdown",
                                        options=[],
                                        placeholder="Select Platform",
                                        searchable=True,
                                    ),
                                ]
                            ),
                        ],
                        className="g-3",
                    ),

                    html.Div(id="scmovir-reference-feedback", className="mt-3"),
                    html.Div(
                        [
                            html.Div(id="scmovir-reference-results-message", className="mb-2"),
                            dbc.Accordion(
                                id="scmovir-reference-accordion",
                                children=[],
                                always_open=True,
                                start_collapsed=True,
                            ),
                        ],
                        id="scmovir-reference-results",
                        className="mt-3",
                    ),
                        dcc.Loading(
                            type="default",
                            children=html.Div(
                                id="scmovir-download-action-loading-signal",
                                style={"display": "none"},
                            ),
                        ),
                ],
            ),
        ]
    )