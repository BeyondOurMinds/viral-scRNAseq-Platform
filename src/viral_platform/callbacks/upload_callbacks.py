import os

from dash import Input, Output, html
import dash_uploader as du

from viral_platform.io.loaders import load_file_from_path

def register_upload_callbacks(app):
    # Callback using dash_uploader's built-in callback decorator to process uploaded files
    # This callback is triggered when a file upload is completed. It reads the uploaded .h5ad file, extracts basic information about the dataset, and updates the UI with the results.
    @du.callback(Output("output-data-upload", "children"), id="file-uploader")
    def process_uploaded_file(file_paths):
        if not file_paths:
            return html.P("No file uploaded yet.")

        file_path = file_paths[0]
        filename = os.path.basename(file_path)
        print(f"Chunked upload completed: {file_path}")

        try:
            adata = load_file_from_path(file_path)
        except Exception as exc:
            return html.Div([
                html.H5(f"Uploaded file: {filename}"),
                html.P(f"Failed to read file: {exc}"),
            ])

        return html.Div([
            html.H5(f"Uploaded file: {filename}"),
            html.P(f"Loaded h5ad file with {adata.n_obs} cells and {adata.n_vars} genes."),
        ])
    
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

        return "File processed. See upload result below."