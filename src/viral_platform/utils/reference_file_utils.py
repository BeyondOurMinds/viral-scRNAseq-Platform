from collections.abc import Callable
from pathlib import Path
import sqlite3

from viral_platform.scmovir.app_paths import get_datasets_dir, get_scmovir_database_path


def scmovir_database_path() -> Path:
    """Return the local scMOVIR SQLite database path."""

    return get_scmovir_database_path()


def read_downloaded_reference_filenames(
    filename_predicate: Callable[[str], bool],
) -> list[str]:
    """Return downloaded reference filenames that satisfy a filename predicate."""

    return list(
        read_downloaded_reference_file_map(
            filename_predicate
        ).keys()
    )


def read_downloaded_reference_file_map(
    filename_predicate: Callable[[str], bool],
) -> dict[str, Path]:
    """Return downloaded reference files as {filename: resolved_local_path}."""

    db_path = scmovir_database_path()

    if not db_path.exists():
        return {}

    datasets_dir = get_datasets_dir()

    conn = None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT filename
            FROM files
            WHERE is_downloaded = 1
            ORDER BY filename
            """
        ).fetchall()

    except sqlite3.Error:
        return {}

    finally:
        if conn is not None:
            conn.close()

    resolved_files: dict[str, Path] = {}

    for row in rows:
        filename = (row["filename"] or "").strip()

        if not filename or not filename_predicate(filename):
            continue

        resolved_path = datasets_dir / filename

        if not resolved_path.exists():
            continue

        if filename not in resolved_files:
            resolved_files[filename] = resolved_path

    return resolved_files