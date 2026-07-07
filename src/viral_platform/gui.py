import logging

from viral_platform.app import create_app
from viral_platform.callbacks import register_sidebar_callbacks, register_upload_callbacks, register_qc_callbacks, register_preprocessing_callbacks, register_differential_expression_callbacks, register_vd_callbacks, register_viral_burden_callbacks
from viral_platform.layout.layout import create_layout

logger = logging.getLogger(__name__)

class ViralApp:
    def __init__(self):
        self.app = create_app()
        self.app.layout = create_layout()
        register_sidebar_callbacks(self.app)
        register_upload_callbacks(self.app)
        register_qc_callbacks(self.app)
        register_preprocessing_callbacks(self.app)
        register_differential_expression_callbacks(self.app)
        register_vd_callbacks(self.app)
        register_viral_burden_callbacks(self.app)
        logger.info("ViralApp initialized and callbacks registered.")

    def run(self):
        try:
            logger.info("Starting Dash server in debug mode.")
            self.app.run(debug=True)
        except Exception:
            logger.exception("Dash server failed to start or crashed during runtime.")
            raise
