from dash import Dash
import dash_uploader as du
import dash_bootstrap_components as dbc
import logging
import os
from pathlib import Path

from viral_platform.utils.logging_config import configure_logging


UPLOAD_FOLDER = "./.upload_cache"
logger = logging.getLogger(__name__)


def _resolve_assets_folder():
    """Use package-local assets so the logos and shell CSS travel together."""
    return Path(__file__).resolve().parent / "assets"


def create_app():
    configure_logging()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    pages_folder = Path(__file__).resolve().parent / "pages"
    assets_folder = _resolve_assets_folder()

    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        use_pages=True,
        pages_folder=str(pages_folder),
        assets_folder=str(assets_folder),
    )
    app.config.suppress_callback_exceptions = True
    du.configure_upload(app, UPLOAD_FOLDER, use_upload_id=True)
    logger.info("Dash app initialized. Upload folder: %s", UPLOAD_FOLDER)
    return app