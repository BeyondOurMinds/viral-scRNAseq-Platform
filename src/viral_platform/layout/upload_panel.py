from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_uploader as du


# Function to create the upload panel layout
def create_upload_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "borderRadius": "5px",
            "border": "1px solid #000000",
            "margin": "0 0 20px 0",
        },
        children=[
            html.H2("Upload Data"),
            dbc.Container([
                dbc.Row([
                    # The file uploader component from dash_uploader, styled to fit the panel design. It allows users to drag and drop files or select them manually, with specific settings for file types and size limits.
                    dbc.Col(du.Upload(
                        id="file-uploader",
                        text="Drag and Drop or Select File",
                        text_completed="Uploaded: ",
                        max_file_size=4096, # 4GB limit for files
                        chunk_size=5, # 5MB chunk size for uploads
                        filetypes=["h5ad"],
                        default_style={
                            "width": "98%",
                            "minHeight": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px 0",
                            "padding": "0 10px",
                        },
                    )),
                ]),
            ]),
            html.Div(
                id="file-input",
                children="No file uploaded",
                style={"textAlign": "center", "width": "100%", "color": "#6c757d"},
            ),
            dcc.Loading(
                type="default",
                children=html.Div(id='output-data-upload')
            ),
        ],
        id="upload-panel"
    )