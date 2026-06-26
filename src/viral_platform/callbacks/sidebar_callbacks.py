from dash import Input, Output, State, no_update


_HASH_TO_TAB = {
    "#qc-panel": "QC-tab",
    "#preprocess-panel": "QC-tab",
    "#differential-expression-panel": "DE-tab",
}


def register_sidebar_callbacks(app):
    @app.callback(Output("sidebar", "hidden"), Input("toggle-button", "n_clicks"))
    def toggle_sidebar_visibility(n_clicks):
        if not n_clicks:
            return True

        return n_clicks % 2 == 0

    @app.callback(
        Output("layout-tabs", "active_tab"),
        Input("page-location", "hash"),
        State("layout-tabs", "active_tab"),
    )
    def sync_active_tab_from_hash(location_hash, current_active_tab):
        if not location_hash:
            return current_active_tab or "QC-tab"

        return _HASH_TO_TAB.get(location_hash, no_update)
