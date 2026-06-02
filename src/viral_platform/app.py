from dash import Dash
import dash_uploader as du


UPLOAD_FOLDER = "./.upload_cache"

def create_app():
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.config.suppress_callback_exceptions = True
    du.configure_upload(app, UPLOAD_FOLDER, use_upload_id=True)
    return app