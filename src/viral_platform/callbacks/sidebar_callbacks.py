from dash import Input, Output


def register_sidebar_callbacks(app):
    @app.callback(Output("sidebar", "hidden"), Input("toggle-button", "n_clicks"))
    def toggle_sidebar_visibility(n_clicks):
        if not n_clicks:
            return True

        return n_clicks % 2 == 0
