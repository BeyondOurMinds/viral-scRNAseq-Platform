from dash import Dash
import dash_uploader as du
import dash_bootstrap_components as dbc
import logging
import os

from viral_platform.utils.logging_config import configure_logging


UPLOAD_FOLDER = "./.upload_cache"
logger = logging.getLogger(__name__)

def create_app():
    configure_logging()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
    )
    app.config.suppress_callback_exceptions = True
    du.configure_upload(app, UPLOAD_FOLDER, use_upload_id=True)
    logger.info("Dash app initialized. Upload folder: %s", UPLOAD_FOLDER)
    return app