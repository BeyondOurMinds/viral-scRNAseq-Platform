from dash import dcc, html
import dash_bootstrap_components as dbc


_PANEL_STYLE = {
    "backgroundColor": "#e9ecef",
    "padding": "20px",
    "borderRadius": "5px",
    "border": "1px solid #000000",
    "margin": "0 0 20px 0",
}


def create_scmovir_download_manager_panel():
    return html.Div(
        style=_PANEL_STYLE,
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(
                                    ["2. Download Manager"],
                                    style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
                                ),
                                html.P(
                                    "Manage downloaded reference files.",
                                    style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
                                ),
                            ]
                        )
                    )
                ]
            ),
            html.Div(id="scmovir-download-manager-feedback", className="mb-2"),
            html.Div(id="scmovir-download-manager-content"),
            dcc.Loading(
                type="default",
                children=html.Div(
                    id="scmovir-remove-action-loading-signal",
                    style={"display": "none"},
                ),
            ),
            html.Div(
                dbc.Button(
                    "Remove Selected",
                    id="scmovir-manager-remove-button",
                    color="danger",
                    n_clicks=0,
                ),
                className="d-flex justify-content-end mt-3",
            ),
        ],
    )