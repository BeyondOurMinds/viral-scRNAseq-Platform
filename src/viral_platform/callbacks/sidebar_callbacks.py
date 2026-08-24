from dash import Input, Output

from viral_platform.layout.navigation import NAV_ITEMS
from viral_platform.layout.sidebar import path_to_token
from viral_platform.state.dataset_store import get_working_dataset

_SIDEBAR_EXPANDED_WIDTH = "280px"
_SIDEBAR_COLLAPSED_WIDTH = "88px"


_LINK_CLASS_OUTPUTS = [
    Output(f"sidebar-link-{path_to_token(item['path'])}", "className")
    for item in NAV_ITEMS
]
_LINK_LABEL_STYLE_OUTPUTS = [
    Output(f"sidebar-link-label-{path_to_token(item['path'])}", "style")
    for item in NAV_ITEMS
]


def register_sidebar_callbacks(app):
    @app.callback(
        *_LINK_CLASS_OUTPUTS,
        Input("app-location", "pathname"),
    )
    def set_active_sidebar_link(pathname):
        """Apply active CSS class to the link matching the current route."""
        current_path = pathname or "/"

        def _is_active(item_path):
            if item_path == "/":
                return current_path == "/"
            return current_path == item_path

        return tuple(
            "sidebar-link active" if _is_active(item["path"]) else "sidebar-link"
            for item in NAV_ITEMS
        )

    @app.callback(
        Output("app-sidebar", "style"),
        Output("app-content-shell", "style"),
        Output("sidebar-brand-copy", "style"),
        Output("sidebar-footer", "style"),
        *_LINK_LABEL_STYLE_OUTPUTS,
        Input("sidebar-collapse-button", "n_clicks"),
    )
    def toggle_sidebar_collapse(n_clicks):
        """Collapse/expand sidebar by width and label visibility in one callback."""
        collapsed = bool(n_clicks and n_clicks % 2 == 1)

        if collapsed:
            sidebar_style = {"width": _SIDEBAR_COLLAPSED_WIDTH}
            content_style = {
                "marginLeft": _SIDEBAR_COLLAPSED_WIDTH,
                "width": f"calc(100% - {_SIDEBAR_COLLAPSED_WIDTH})",
            }
            label_style = {"display": "none"}
            brand_copy_style = {"display": "none"}
            footer_style = {"display": "none"}
        else:
            sidebar_style = {"width": _SIDEBAR_EXPANDED_WIDTH}
            content_style = {
                "marginLeft": _SIDEBAR_EXPANDED_WIDTH,
                "width": f"calc(100% - {_SIDEBAR_EXPANDED_WIDTH})",
            }
            label_style = {"display": "inline"}
            brand_copy_style = {"display": "block"}
            footer_style = {"display": "block"}

        return (sidebar_style, content_style, brand_copy_style, footer_style, *tuple(label_style for _ in NAV_ITEMS))

    @app.callback(
        Output("sidebar-dataset-status", "children"),
        Output("sidebar-dataset-metrics", "children"),
        Input("active-dataset-version", "data"),
    )
    def update_dataset_summary(_dataset_version):
        """Show the current dataset filename and size metrics in the sidebar."""
        adata = get_working_dataset()
        if adata is None:
            return "No dataset loaded", ""

        filename = adata.uns.get("source_filename")
        status = str(filename) if filename else "Loaded dataset"
        metrics = f"{adata.n_obs} cells • {adata.n_vars} genes"
        return status, metrics
