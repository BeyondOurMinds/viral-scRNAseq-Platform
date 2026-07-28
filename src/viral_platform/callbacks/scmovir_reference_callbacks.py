from pathlib import Path
import sqlite3

from dash import ALL, Input, Output, State, ctx, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from viral_platform.scmovir.reference_database import ReferenceDatabase
from viral_platform.scmovir.reference_manager import ReferenceManager


_FIELDS = ("virus_species", "disease", "tissue", "platform")


def _database_path() -> Path:
    return Path(__file__).resolve().parent.parent / "scmovir" / "scmovir.db"


def _normalize_value(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _read_project_rows():
    db = ReferenceDatabase(_database_path())
    try:
        try:
            rows = db.cursor.execute(
                """
                SELECT virus_species, disease, tissue, platform
                FROM projects
                """
            ).fetchall()
        except sqlite3.Error:
            rows = []
    finally:
        db.close()
    return rows


def _build_project_query(filters):
    query = """
        SELECT project_id, accession, title, virus_species, disease, tissue
        FROM projects
        WHERE 1=1
    """
    params = []
    for field in _FIELDS:
        value = _normalize_value(filters.get(field))
        if value:
            query += f" AND {field} = ?"
            params.append(value)
    query += " ORDER BY accession"
    return query, params


def _read_projects_with_filters(filters):
    db = ReferenceDatabase(_database_path())
    try:
        query, params = _build_project_query(filters)
        return db.cursor.execute(query, params).fetchall()
    except sqlite3.Error:
        return []
    finally:
        db.close()


def _read_project_files(project_id):
    db = ReferenceDatabase(_database_path())
    try:
        return db.cursor.execute(
            """
            SELECT file_type, filename, is_downloaded
            FROM files
            WHERE project_id = ?
            ORDER BY file_type
            """,
            (project_id,),
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        db.close()


def _matches_filters(row, filters):
    for field, expected in filters.items():
        if expected and _normalize_value(row[field]) != expected:
            return False
    return True


def _build_options(values):
    return [{"label": value, "value": value} for value in sorted(values, key=str.casefold)]


def _normalize_active_items(active_item):
    if active_item is None:
        return []
    if isinstance(active_item, list):
        return active_item
    return [active_item]


def _project_metadata_box(project):
    return dbc.Card(
        dbc.CardBody(
            [
                html.P([html.Strong("Title: "), project["title"] or "N/A"], className="mb-2"),
                html.P([html.Strong("Disease: "), project["disease"] or "N/A"], className="mb-1"),
                html.P([html.Strong("Virus: "), project["virus_species"] or "N/A"], className="mb-1"),
                html.P([html.Strong("Tissue: "), project["tissue"] or "N/A"], className="mb-0"),
            ]
        ),
        className="mb-3",
    )


def _project_files_table(project_id, files):
    rows = []
    for file_row in files:
        downloaded = bool(file_row["is_downloaded"])
        rows.append(
            html.Tr(
                [
                    html.Td(file_row["filename"]),
                    html.Td(str(downloaded)),
                    html.Td(
                        dbc.Checkbox(
                            id={
                                "type": "scmovir-file-select",
                                "project_id": project_id,
                                "file_type": file_row["file_type"],
                            },
                            value=False,
                        )
                    ),
                ]
            )
        )

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Table(
                    [
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Project Files"),
                                    html.Th("Downloaded"),
                                    html.Th("Select"),
                                ]
                            )
                        ),
                        html.Tbody(rows),
                    ],
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="mb-0",
                )
            ]
        ),
        className="mb-3",
    )


def _build_project_item(project):
    project_id = project["project_id"]
    files = _read_project_files(project_id)

    return dbc.AccordionItem(
        item_id=project_id,
        title=project["accession"] or project_id,
        children=[
            _project_metadata_box(project),
            _project_files_table(project_id, files),
            html.Div(
                [
                    dbc.Button(
                        "Download",
                        id={"type": "scmovir-download-button", "project_id": project_id},
                        color="success",
                        className="me-2",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        "Remove",
                        id={"type": "scmovir-remove-button", "project_id": project_id},
                        color="danger",
                        n_clicks=0,
                    ),
                ],
                className="d-flex justify-content-end",
            ),
        ],
    )


def register_scmovir_reference_callbacks(app):
    @app.callback(
        Output("scmovir-virus-dropdown", "options"),
        Output("scmovir-disease-dropdown", "options"),
        Output("scmovir-tissue-dropdown", "options"),
        Output("scmovir-platform-dropdown", "options"),
        Output("scmovir-virus-dropdown", "value"),
        Output("scmovir-disease-dropdown", "value"),
        Output("scmovir-tissue-dropdown", "value"),
        Output("scmovir-platform-dropdown", "value"),
        Input("scmovir-virus-dropdown", "value"),
        Input("scmovir-disease-dropdown", "value"),
        Input("scmovir-tissue-dropdown", "value"),
        Input("scmovir-platform-dropdown", "value"),
        prevent_initial_call=False,
    )
    def sync_scmovir_dropdowns(virus_value, disease_value, tissue_value, platform_value):
        rows = _read_project_rows()

        selected = {
            "virus_species": _normalize_value(virus_value),
            "disease": _normalize_value(disease_value),
            "tissue": _normalize_value(tissue_value),
            "platform": _normalize_value(platform_value),
        }

        options_by_field = {}
        for field in _FIELDS:
            other_filters = {name: value for name, value in selected.items() if name != field}
            valid_values = {
                normalized
                for row in rows
                if _matches_filters(row, other_filters)
                for normalized in [_normalize_value(row[field])]
                if normalized
            }
            options_by_field[field] = _build_options(valid_values)

        resolved_values = {}
        for field in _FIELDS:
            available_values = {option["value"] for option in options_by_field[field]}
            current_value = selected[field]
            resolved_values[field] = current_value if current_value in available_values else None

        return (
            options_by_field["virus_species"],
            options_by_field["disease"],
            options_by_field["tissue"],
            options_by_field["platform"],
            resolved_values["virus_species"],
            resolved_values["disease"],
            resolved_values["tissue"],
            resolved_values["platform"],
        )

    @app.callback(
        Output("scmovir-active-filters", "data"),
        Output("scmovir-reference-feedback", "children", allow_duplicate=True),
        Input("find-scmovir-reference-button", "n_clicks"),
        State("scmovir-virus-dropdown", "value"),
        State("scmovir-disease-dropdown", "value"),
        State("scmovir-tissue-dropdown", "value"),
        State("scmovir-platform-dropdown", "value"),
        prevent_initial_call=True,
    )
    def store_active_filters(n_clicks, virus_value, disease_value, tissue_value, platform_value):
        if not n_clicks:
            raise PreventUpdate

        filters = {
            "virus_species": _normalize_value(virus_value),
            "disease": _normalize_value(disease_value),
            "tissue": _normalize_value(tissue_value),
            "platform": _normalize_value(platform_value),
        }

        if not any(filters.values()):
            return (
                no_update,
                dbc.Alert(
                    "Select at least one filter before searching to avoid loading the entire reference catalog.",
                    color="warning",
                    className="mt-2 mb-0",
                ),
            )

        return filters, ""

    @app.callback(
        Output("scmovir-reference-results-message", "children"),
        Output("scmovir-reference-accordion", "children"),
        Output("scmovir-reference-accordion", "active_item"),
        Input("scmovir-active-filters", "data"),
        Input("scmovir-refresh-token", "data"),
        State("scmovir-reference-accordion", "active_item"),
        prevent_initial_call=False,
    )
    def render_scmovir_results(filters, _refresh_token, active_item):
        if filters is None:
            return html.P("Choose filters (optional) and click Find Reference(s).", className="mb-0"), [], []

        projects = _read_projects_with_filters(filters)
        if not projects:
            return html.P("No projects found for the selected criteria.", className="mb-0"), [], []

        project_ids = [project["project_id"] for project in projects]
        open_items = [item for item in _normalize_active_items(active_item) if item in project_ids]
        items = [_build_project_item(project) for project in projects]
        return "", items, open_items

    @app.callback(
        Output("scmovir-refresh-token", "data"),
        Output("scmovir-reference-feedback", "children", allow_duplicate=True),
        Input({"type": "scmovir-download-button", "project_id": ALL}, "n_clicks"),
        Input({"type": "scmovir-remove-button", "project_id": ALL}, "n_clicks"),
        State({"type": "scmovir-file-select", "project_id": ALL, "file_type": ALL}, "value"),
        State({"type": "scmovir-file-select", "project_id": ALL, "file_type": ALL}, "id"),
        State("scmovir-refresh-token", "data"),
        prevent_initial_call=True,
    )
    def update_project_files(_download_clicks, _remove_clicks, selected_values, selected_ids, refresh_token):
        trigger = ctx.triggered_id
        if not isinstance(trigger, dict):
            raise PreventUpdate

        project_id = trigger.get("project_id")
        trigger_type = trigger.get("type")
        if not project_id or trigger_type not in {"scmovir-download-button", "scmovir-remove-button"}:
            raise PreventUpdate

        selected_file_types = [
            checkbox_id["file_type"]
            for checkbox_id, is_selected in zip(selected_ids, selected_values)
            if checkbox_id.get("project_id") == project_id and bool(is_selected)
        ]

        if not selected_file_types:
            return refresh_token, dbc.Alert("Select at least one file for this project.", color="warning", className="mt-2 mb-0")

        db = ReferenceDatabase(_database_path())
        manager = ReferenceManager(db)
        try:
            if trigger_type == "scmovir-download-button":
                success_count = 0
                for file_type in selected_file_types:
                    if manager.download_file(project_id, file_type):
                        success_count += 1
                message = f"Downloaded {success_count}/{len(selected_file_types)} selected file(s)."
                color = "success" if success_count else "danger"
            else:
                for file_type in selected_file_types:
                    manager.remove_downloaded_file(project_id, file_type)
                message = f"Removed {len(selected_file_types)} selected file(s)."
                color = "secondary"
        finally:
            db.close()

        next_token = (refresh_token or 0) + 1
        return next_token, dbc.Alert(message, color=color, className="mt-2 mb-0")