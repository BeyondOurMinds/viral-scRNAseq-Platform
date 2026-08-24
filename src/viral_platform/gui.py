import logging
import os

from viral_platform.app import create_app
from viral_platform.callbacks import register_sidebar_callbacks, register_upload_callbacks, register_qc_callbacks, register_preprocessing_callbacks, register_differential_expression_callbacks, register_vd_callbacks, register_viral_burden_callbacks, register_isg_callbacks, register_host_virus_interaction_callbacks, register_ccc_callbacks, register_scmovir_reference_callbacks, register_cell_annotation_callbacks, register_pathway_enrichment_callbacks, register_save_callbacks
from viral_platform.layout.layout import create_layout

logger = logging.getLogger(__name__)


class ViralApp:
    def __init__(self):
        self.app = create_app()
        self.app.layout = create_layout()
        register_sidebar_callbacks(self.app)
        register_upload_callbacks(self.app)
        register_save_callbacks(self.app)
        register_qc_callbacks(self.app)
        register_preprocessing_callbacks(self.app)
        register_cell_annotation_callbacks(self.app)
        register_differential_expression_callbacks(self.app)
        register_pathway_enrichment_callbacks(self.app)
        register_vd_callbacks(self.app)
        register_viral_burden_callbacks(self.app)
        register_isg_callbacks(self.app)
        register_host_virus_interaction_callbacks(self.app)
        register_ccc_callbacks(self.app)
        register_scmovir_reference_callbacks(self.app)
        logger.info("ViralApp initialized and callbacks registered.")

    def run(self):
        try:
            host = os.getenv("HOST", "127.0.0.1")
            port = int(os.getenv("PORT", "8050"))
            display_host = "localhost" if host in {"0.0.0.0", "::", "0:0:0:0:0:0:0:0"} else host

            if hasattr(self.app, "server"):
                self.app.server.logger.disabled = True
                self.app.server.logger.propagate = False

            logging.getLogger("werkzeug").disabled = True

            logger.info(
                "Starting SCJoseki. Open http://%s:%s/ (server bound to %s:%s)",
                display_host,
                port,
                host,
                port,
            )

            self.app.run(
                host=host,
                port=port,
                debug=False,
                use_reloader=False,
                dev_tools_hot_reload=False,
            )
        except Exception:
            logger.exception("Dash server failed to start or crashed during runtime.")
            raise
