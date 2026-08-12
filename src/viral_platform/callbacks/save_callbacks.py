import base64
import logging

from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

from viral_platform.io.session_saves import (
    create_optional_exports_bundle,
    list_saved_sessions,
    save_current_session,
)

logger = logging.getLogger(__name__)


def _build_save_options():
    options = []
    for session in list_saved_sessions():
        options.append({"label": session["name"], "value": session["name"]})
    return options


def register_save_callbacks(app):
    @app.callback(
        Output("load-save-dropdown", "options"),
        Output("load-save-dropdown", "value"),
        Input("app-location", "pathname"),
        Input("refresh-saves-btn", "n_clicks"),
        Input("saves-refresh-token", "data"),
        State("load-save-dropdown", "value"),
        prevent_initial_call=False,
    )
    def refresh_saved_session_options(pathname, _refresh_clicks, _save_token, current_value):
        if pathname != "/upload":
            raise PreventUpdate

        options = _build_save_options()
        values = {option["value"] for option in options}
        if current_value in values:
            return options, current_value
        return options, (options[0]["value"] if options else None)

    @app.callback(
        Output("save-session-status", "children"),
        Output("saves-refresh-token", "data"),
        Input("save-current-session-btn", "n_clicks"),
        State("save-folder-name-input", "value"),
        State("saves-refresh-token", "data"),
        prevent_initial_call=True,
    )
    def save_session_to_project_folder(n_clicks, save_name, refresh_token):
        if not n_clicks:
            raise PreventUpdate

        try:
            result = save_current_session(save_name)
        except Exception as exc:
            logger.exception("Session save failed.")
            return html.P(f"Save failed: {exc}", style={"color": "#b02a37"}), refresh_token or 0

        details = [
            html.P(
                f"Saved session '{result['name']}' to {result['folder']}.",
                style={"color": "#146c43"},
            )
        ]

        for warning in result.get("warnings", []):
            details.append(html.P(warning, style={"color": "#856404"}))

        return html.Div(details), int(refresh_token or 0) + 1

    @app.callback(
        Output("optional-export-download", "data"),
        Output("optional-export-status", "children"),
        Input("export-optional-files-btn", "n_clicks"),
        State("save-export-options-checklist", "value"),
        prevent_initial_call=True,
    )
    def download_optional_exports(n_clicks, selected_options):
        if not n_clicks:
            raise PreventUpdate

        options = set(selected_options or [])
        include_metadata = "metadata_csv" in options
        include_tables_figures = "tables_figures" in options
        include_log = "log_file" in options

        try:
            filename, payload, notes = create_optional_exports_bundle(
                include_metadata=include_metadata,
                include_tables_figures=include_tables_figures,
                include_log=include_log,
            )
        except Exception as exc:
            logger.exception("Optional export bundle failed.")
            return None, html.P(f"Optional export failed: {exc}", style={"color": "#b02a37"})

        note_items = [html.P("Optional export bundle prepared.", style={"color": "#146c43"})]
        note_items.extend(html.P(note) for note in notes)

        content = base64.b64encode(payload).decode("ascii")
        return {
            "content": content,
            "filename": filename,
            "type": "application/zip",
            "base64": True,
        }, html.Div(note_items)
