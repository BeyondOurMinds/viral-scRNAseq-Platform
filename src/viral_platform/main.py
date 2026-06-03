import logging

from viral_platform.gui import ViralApp

logger = logging.getLogger(__name__)

def main():
    try:
        app = ViralApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    except Exception:
        logger.exception("Application terminated due to an unexpected error.")
        raise


if __name__ == "__main__":
    main()