from dash import html, dcc
import dash_bootstrap_components as dbc

def create_viral_burden_panel():
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
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            html.H4(
                                ["2. Viral Burden Analysis"],
                                style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                            ),
                            html.P(
                                "Calculate the viral burden from the detected viral genes",
                                style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    dbc.Button("Run Viral Burden Analysis", id="run-viral-burden-analysis-button", n_clicks=0, color="primary", className="mb-3"),
                    width="auto"
                )
            ]),

            # loading signal
            dcc.Loading(
                type="default",
                children=html.Div(id="viral-burden-loading-signal", style={"display": "none"}),
            ),

            # results container
            html.Div(
                id="viral-burden-results-container",
                children=[
                    html.P(
                        "No viral burden results yet. Run the analysis to see results here.",
                        style={"color": "#6c757d", "fontSize": "14px"},
                    )
                ],
            ),
            # Viral Burden Associations
            html.Div(
                id="viral-burden-associations-container",
                children=[
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                id="viral-burden-temp-container",
                                children=[
                                    html.H4(
                                        ["2.1 Viral Burden Association"],
                                        style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                                    ),
                                    html.P(
                                        "Find viral burden associations or some shit",
                                        style={"color": "#6c757d", "marginBottom": "16px", "marginTop": "8px", "fontSize": "14px"},
                                    ),
                                ],
                            ),
                        ),
                        dbc.Col(
                            dbc.Button("Run Viral Burden Association", id="run-viral-burden-association-button", n_clicks=0, color="primary", className="mb-3"),
                            width="auto"
                        )
                    ]),
                ],
                hidden=True,
                style={"marginTop": "20px", "padding": "10px", "border": "1px solid #dee2e6", "borderRadius": "5px"},
            )
        ]
    )