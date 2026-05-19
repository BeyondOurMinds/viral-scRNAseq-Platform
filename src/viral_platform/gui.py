from viral_platform.app import create_app
from viral_platform.layout import create_layout

class ViralApp:
    def __init__(self):
        self.app = create_app()
        self.app.layout = create_layout()

    def run(self):
        self.app.run(debug=True)
