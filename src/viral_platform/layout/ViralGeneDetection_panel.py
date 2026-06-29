from dash import html, dcc
import dash_bootstrap_components as dbc

def create_viral_gene_detection_panel():
    def help_icon():
        return html.Span(
            "?",
            style={
                "display": "inline-flex",
                "alignItems": "center",
                "justifyContent": "center",
                "width": "18px",
                "height": "18px",
                "borderRadius": "50%",
                "border": "1.5px solid #6c757d",
                "fontSize": "11px",
                "color": "#6c757d",
                "cursor": "pointer",
                "marginLeft": "6px",
                "verticalAlign": "middle",
            },
        )
    
    # ── Detection method cards ─────────────────────────────────────────────
    auto_card = dbc.Col(
        html.Div(
            id="automatic-detection-card",
            children=
            [
                html.Div(
                    id="automatic-detection-card-title",
                    children=html.Span(
                    ["Automatic Detection"],
                    ),
                    style={"fontWeight": "600", "color": "#212529"},
                ),
                html.P(
                    "Search using built-in virus gene lists",
                    style={"fontSize": "13px", "color": "#6c757d"},
                ),
            ],
            style={
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#fff",
                "cursor": "pointer",
            },
        ),
    )

    custom_card = dbc.Col(
        html.Div(
            id="custom-detection-card",
            children=
            [
                html.Div(
                    id="custom-detection-card-title",
                    children=html.Span(
                    ["Custom Detection"],
                    ),
                    style={"fontWeight": "600", "color": "#212529"},
                ),
                html.P(
                    "Provide your own list of viral genes",
                    style={"fontSize": "13px", "color": "#6c757d"},
                ),
            ],
            style={
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#fff",
                "cursor": "pointer",
            },
        ),
    )

    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            # title
            html.Div(
                [
                    html.H4(
                        ["1. Viral Gene Detection", help_icon()],
                        style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                    ),
                    html.P(
                        "Automatically detect viral genes using known virus gene lists, or provide your own gene list.",
                        style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                    ),
                ]
            ),
            # detection method selection
            dbc.Row([
                dbc.Col(
                    [
                        html.Div(
                            ["Detection Method", help_icon()],
                            style={
                                "fontWeight": "600",
                                "marginBottom": "10px",
                                "display": "flex",
                                "alignItems": "center",
                            },
                        ),
                        dbc.Row([
                            dbc.Col(
                                dbc.RadioItems(
                                    id="detection-method-radio",
                                    options=[
                                        {"label": auto_card, "value": "automatic"},
                                        {"label": custom_card, "value": "custom"},
                                    ],
                                    value="automatic",
                                    inline=True,
                                ),
                            )
                        ]),
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id="custom-gene-list-container",
                                    children=[
                                        dbc.Textarea(
                                            id="custom-gene-list-input",
                                            placeholder="Enter custom viral gene list (comma-separated)",
                                            wrap=True,
                                        ),
                                    ],
                                    style={"marginTop": "10px"},
                                    hidden=True,
                                )
                            )
                        ])
                    ]
                ),
                # Virus Selection Dropdown
                dbc.Col([
                    dbc.Row([
                        html.Div(
                            ["Select Virus ", html.Span("(Optional)", style={"color": "#6c757d", "fontWeight": "400"}), help_icon()],
                            style={
                                "fontWeight": "600",
                                "marginBottom": "10px",
                                "display": "flex",
                                "alignItems": "center",
                                "gap": "4px",
                            },
                        ),
                        dcc.Dropdown(
                            id="virus-select-dropdown",
                            options=[{"label": "Auto-detect (search all known viruses)", "value": "__auto__"},
                                     {"label": "Epstein-Barr Virus (EBV)", "value": "EBV"},
                                     ],
                            value="__auto__",
                            clearable=False,
                        ),
                        html.P(
                            "Search all supported viruses for matches in the dataset.",
                            style={"fontSize": "12px", "color": "#6c757d", "marginTop": "6px"},
                        ),
                    ]),
                    dbc.Row([
                        dbc.Button("Run Viral Gene Detection", id="run-viral-gene-detection-button", n_clicks=0, color="primary", className="mb-3"),
                    ])
                ])
            ],
            className="mb-3",
            ),
        ]
    )