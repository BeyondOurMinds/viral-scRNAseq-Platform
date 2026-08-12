from dash import Dash
import dash_uploader as du
import dash_bootstrap_components as dbc
import logging
import os
from pathlib import Path
import subprocess
import sys
from viral_platform.scmovir.app_paths import get_app_data_dir

from viral_platform.utils.logging_config import configure_logging


UPLOAD_FOLDER = get_app_data_dir() / ".upload_cache"
logger = logging.getLogger(__name__)


def _resolve_assets_folder():
    """Use package-local assets so the logos and shell CSS travel together."""
    return Path(__file__).resolve().parent / "assets"


def _open_folder_in_file_manager(folder_path):
    """Open a local folder in the platform file manager."""
    if sys.platform.startswith("win"):
        os.startfile(str(folder_path))
        return

    if sys.platform == "darwin":
        subprocess.Popen(["open", str(folder_path)])
        return

    subprocess.Popen(["xdg-open", str(folder_path)])


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

    @app.server.route("/open-saves-folder")
    def open_saves_folder():
        from viral_platform.io.session_saves import get_saves_dir

        saves_dir = get_saves_dir()
        try:
            _open_folder_in_file_manager(saves_dir)
            return (
                f"Opened saves folder: {saves_dir}",
                200,
                {"Content-Type": "text/plain; charset=utf-8"},
            )
        except Exception as exc:
            logger.exception("Failed to open saves folder: %s", saves_dir)
            return (
                f"Could not open saves folder: {exc}",
                500,
                {"Content-Type": "text/plain; charset=utf-8"},
            )

    logger.info("Dash app initialized. Upload folder: %s", UPLOAD_FOLDER)
    return app