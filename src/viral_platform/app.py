from dash import Dash
import dash_uploader as du


UPLOAD_FOLDER = "./.upload_cache"

def create_app():
    app = Dash(__name__)
    du.configure_upload(app, UPLOAD_FOLDER, use_upload_id=True)
    return app