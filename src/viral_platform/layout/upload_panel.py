from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_uploader as du


# Function to create the upload panel layout
def create_upload_panel():
    return html.Div(
        style={
            "backgroundColor": "#eff7ff",
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
                        max_file_size=65536, # 64GB limit for files
                        chunk_size=5, # 5MB chunk size for uploads
                        filetypes=["h5ad", "zip", "h5", "csv", "tsv", "txt"], # Allowed file types
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
            html.Hr(),
            html.H3("Export save"),
            html.P(
                "Save the current working AnnData object to the project saves folder. "
                "The folder name below is the save name."
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(
                            id="save-folder-name-input",
                            placeholder="Enter save folder name",
                            type="text",
                        ),
                        md=8,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Save Current Session",
                            id="save-current-session-btn",
                            color="primary",
                            n_clicks=0,
                            className="w-100",
                        ),
                        md=4,
                    ),
                ],
                className="g-2",
            ),
            html.Div(
                [
                    html.Span("Saved sessions live in: "),
                    html.A(
                        "Open saves folder",
                        id="open-saves-folder-link",
                        href="/open-saves-folder",
                        target="_blank",
                    ),
                ],
                style={"marginTop": "10px"},
            ),
            html.H5("Optional exports"),
            dcc.Checklist(
                id="save-export-options-checklist",
                options=[
                    {"label": "Metadata CSV", "value": "metadata_csv"},
                    {"label": "Tables/Figures bundle (CSV + SVG)", "value": "tables_figures"},
                    {"label": "Log file", "value": "log_file"},
                ],
                value=[],
                style={"marginBottom": "10px"},
            ),
            dbc.Button(
                "Download Optional Exports",
                id="export-optional-files-btn",
                color="secondary",
                n_clicks=0,
            ),
            html.Div(id="save-session-status", style={"marginTop": "12px"}),
            html.Div(id="optional-export-status", style={"marginTop": "8px"}),
            dcc.Download(id="optional-export-download"),
            dcc.Store(id="saves-refresh-token", data=0),
            html.Hr(),
            html.H3("Load save"),
            html.P("Load a saved session from the project saves folder."),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="load-save-dropdown",
                            options=[],
                            placeholder="Select a saved session",
                            clearable=True,
                        ),
                        md=7,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Refresh",
                            id="refresh-saves-btn",
                            color="light",
                            n_clicks=0,
                            className="w-100",
                        ),
                        md=2,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Load Selected Save",
                            id="load-selected-save-btn",
                            color="success",
                            n_clicks=0,
                            className="w-100",
                        ),
                        md=3,
                    ),
                ],
                className="g-2",
            ),
            html.Div(id="load-save-status", style={"marginTop": "12px"}),
        ],
        id="upload-panel"
    )