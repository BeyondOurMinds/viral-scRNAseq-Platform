from dash import html, dcc
import dash_bootstrap_components as dbc

def create_upload_panel():
    return html.Div(
        style={
            "backgroundColor": "#e9ecef",
            "padding": "20px",
            "margin": "10px",
            "borderRadius": "5px",
        },
        children=[
            html.H2("Upload Data"),
            dbc.Container([
                dbc.Row([
                    dbc.Col(dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px 0'
                        },
                        multiple=False,
                        accept='.csv,.tsv,.xlsx' # tempory file types
                    )),
                ]),
            ]),
            dcc.Input(type="text", id="file-input", value="No File Selected", readOnly=True, style={'textAlign': 'center', 'width': '100%', 'color': '#6c757d'}),
        ],
        id="upload-panel"
    )