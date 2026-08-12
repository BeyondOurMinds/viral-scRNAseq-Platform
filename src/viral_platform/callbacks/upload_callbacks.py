import os
import uuid
import logging
from pathlib import Path

from dash import Input, Output, State, ctx, html, no_update

from viral_platform.app import UPLOAD_FOLDER
from viral_platform.io.session_saves import load_saved_session
from viral_platform.io.loaders import load_file_from_path

logger = logging.getLogger(__name__)

def register_upload_callbacks(app):
    # Use an explicit Dash callback instead of du.callback so we can always
    # return a valid output tuple in multi-page mount/unmount cycles.
    @app.callback(
        Output("output-data-upload", "children"),
        Output("active-dataset-version", "data"),
        Output("load-save-status", "children"),
        Input("file-uploader", "isCompleted"),
        Input("load-selected-save-btn", "n_clicks"),
        State("file-uploader", "fileNames"),
        State("file-uploader", "upload_id"),
        State("load-save-dropdown", "value"),
        prevent_initial_call=False,
    )
    def process_uploaded_file(is_completed, load_clicks, file_names, upload_id, selected_save):
        trigger_id = ctx.triggered_id

        if trigger_id == "load-selected-save-btn":
            if not load_clicks:
                return no_update, no_update, no_update

            try:
                loaded = load_saved_session(selected_save)
            except Exception as exc:
                logger.exception("Failed to load saved session: %s", selected_save)
                return html.P(f"Failed to load save: {exc}"), no_update, html.P(
                    f"Failed to load save: {exc}", style={"color": "#b02a37"}
                )

            return (
                html.Div([
                    html.H5(f"Loaded save: {loaded['name']}"),
                    html.P(
                        f"Loaded dataset with {loaded['cells']} cells and {loaded['genes']} genes."
                    ),
                    html.Div(
                        [html.P(warning) for warning in loaded.get("warnings", [])],
                        style={"color": "#856404"},
                    ),
                ]),
                str(uuid.uuid4()),
                html.P(f"Loaded save '{loaded['name']}'.", style={"color": "#146c43"}),
            )

        if not is_completed:
            # Component mount/navigation can emit a non-complete state. Never
            # return None for a multi-output callback.
            logger.info("Upload callback received non-complete state.")
            return no_update, no_update, no_update

        root_folder = Path(UPLOAD_FOLDER)
        if upload_id:
            root_folder = root_folder / str(upload_id)

        file_paths = []
        if file_names:
            file_paths = [str(root_folder / filename) for filename in file_names]

        if not file_paths:
            logger.info("Upload callback triggered with no files.")
            return html.P("No file uploaded yet."), no_update, no_update

        file_path = file_paths[0]
        filename = os.path.basename(file_path)
        logger.info("Chunked upload completed: %s", file_path)

        try:
            adata = load_file_from_path(file_path)
        except Exception as exc:
            logger.exception("Failed to process uploaded file: %s", filename)
            return (
                html.Div([
                    html.H5(f"Uploaded file: {filename}"),
                    html.P(f"Failed to read file: {exc}"),
                ]),
                no_update,
                no_update,
            )

        logger.info(
            "Successfully processed uploaded file %s (%s cells, %s genes).",
            filename,
            adata.n_obs,
            adata.n_vars,
        )

        sample_count = adata.uns.get("sample_count")
        dataset_message = f"Loaded dataset with {adata.n_obs} cells and {adata.n_vars} genes."
        if sample_count:
            dataset_message = (
                f"Loaded dataset with {adata.n_obs} cells and {adata.n_vars} genes "
                f"from {sample_count} sample(s)."
            )

        return (
            html.Div([
                html.H5(f"Uploaded file: {filename}"),
                html.P(dataset_message),
            ]),
            str(uuid.uuid4()),
            no_update,
        )
    
    # This callback updates the file status text based on the upload result. It listens to changes in the upload output and updates the status message accordingly.
    @app.callback(
        Output("file-input", "children"),
        Input("output-data-upload", "children"),
        prevent_initial_call=False,
    )
    def update_file_status(_upload_output):
        # This keeps status text aligned with current upload result panel.
        if not _upload_output:
            return "No file uploaded"

        logger.info("Upload status updated in UI.")
        return "File processed. See upload result below."