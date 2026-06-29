from dash import Input, Output, State, html, no_update, dash_table, dcc
import dash_bootstrap_components as dbc

def register_vd_callbacks(app):
    @app.callback(
        Output("custom-detection-card", "style"),
        Output("custom-detection-card-title", "style"),
        Output("custom-gene-list-container", "hidden"),
        Input("detection-method-radio", "value"),
    )
    def update_custom_card_style(selected_method):
        if selected_method == "custom":
            return {
                "border": "2px solid #0d6efd",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#f0f6ff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#0d6efd"}, False
        else:
            return {
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#ffffff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#212529"}, True
    
    @app.callback(
        Output("automatic-detection-card", "style"),
        Output("automatic-detection-card-title", "style"),
        Input("detection-method-radio", "value"),
    )
    def update_automatic_card_style(selected_method):
        if selected_method == "automatic":
            return {
                "border": "2px solid #0d6efd",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#f0f6ff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#0d6efd"}
        else:
            return {
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#ffffff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#212529"}