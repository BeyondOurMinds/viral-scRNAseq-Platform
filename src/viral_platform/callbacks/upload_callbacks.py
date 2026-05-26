from dash import Input, Output

def register_upload_callbacks(app):
    @app.callback(
        Output("file-input", "value"),
        Input("upload-data", "contents"),
        Input("upload-data", "filename"),
        Input("upload-data", "last_modified")
    )
    def handle_file_upload(contents, filename, last_modified):
        if contents is not None:
            return f'{filename}'
        return "No file selected"