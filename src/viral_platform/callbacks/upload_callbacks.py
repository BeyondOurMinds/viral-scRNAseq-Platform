import os
import uuid
import logging
from pathlib import Path

from dash import Input, Output, State, html, no_update

from viral_platform.app import UPLOAD_FOLDER
from viral_platform.io.loaders import load_file_from_path

logger = logging.getLogger(__name__)

def register_upload_callbacks(app):
    # Use an explicit Dash callback instead of du.callback so we can always
    # return a valid output tuple in multi-page mount/unmount cycles.
    @app.callback(
        Output("output-data-upload", "children"),
        Output("active-dataset-version", "data"),
        Input("file-uploader", "isCompleted"),
        State("file-uploader", "fileNames"),
        State("file-uploader", "upload_id"),
        prevent_initial_call=False,
    )
    def process_uploaded_file(is_completed, file_names, upload_id):
        if not is_completed:
            # Component mount/navigation can emit a non-complete state. Never
            # return None for a multi-output callback.
            logger.info("Upload callback received non-complete state.")
            return no_update, no_update

        root_folder = Path(UPLOAD_FOLDER)
        if upload_id:
            root_folder = root_folder / str(upload_id)

        file_paths = []
        if file_names:
            file_paths = [str(root_folder / filename) for filename in file_names]

        if not file_paths:
            logger.info("Upload callback triggered with no files.")
            return html.P("No file uploaded yet."), no_update

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