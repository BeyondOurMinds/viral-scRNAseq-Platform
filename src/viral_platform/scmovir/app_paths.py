import os
import shutil
from pathlib import Path


def get_app_data_dir() -> Path:
    if os.name == "nt":
        base_dir = Path(
            os.environ.get(
                "LOCALAPPDATA",
                Path.home() / "AppData" / "Local",
            )
        )
    else:
        base_dir = Path.home() / ".local" / "share"

    app_dir = base_dir / "SCJoseki"
    app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir


def get_datasets_dir() -> Path:
    datasets_dir = get_app_data_dir() / "datasets"
    datasets_dir.mkdir(parents=True, exist_ok=True)

    return datasets_dir


def get_persistent_database_path() -> Path:
    return get_app_data_dir() / "scmovir.db"


def initialize_scmovir_database(
    bundled_database_path: Path,
) -> Path:
    """Create the persistent scMOVIR database from the bundled seed database."""

    persistent_path = get_persistent_database_path()

    if not persistent_path.exists():
        shutil.copy2(
            bundled_database_path,
            persistent_path,
        )

    return persistent_path

def get_scmovir_database_path() -> Path:
    """
    Return the persistent scMOVIR database path.
    """

    bundled_db = (
        Path(__file__).resolve().parent
        / "scmovir.db"
    )

    return initialize_scmovir_database(bundled_db)