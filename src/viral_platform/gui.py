from viral_platform.app import create_app
from viral_platform.callbacks import register_sidebar_callbacks
from viral_platform.callbacks import register_upload_callbacks
from viral_platform.callbacks import register_qc_callbacks
from viral_platform.layout.layout import create_layout

class ViralApp:
    def __init__(self):
        self.app = create_app()
        self.app.layout = create_layout()
        register_sidebar_callbacks(self.app)
        register_upload_callbacks(self.app)
        register_qc_callbacks(self.app)

    def run(self):
        self.app.run(debug=True)
