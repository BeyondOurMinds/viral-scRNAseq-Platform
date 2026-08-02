from collections.abc import Callable
from pathlib import Path
import sqlite3


def scmovir_database_path() -> Path:
    """Return the local scMOVIR SQLite database path."""
    return Path(__file__).resolve().parent.parent / "scmovir" / "scmovir.db"


def read_downloaded_reference_filenames(
    filename_predicate: Callable[[str], bool],
) -> list[str]:
    """Return downloaded reference filenames that satisfy a filename predicate."""
    db_path = scmovir_database_path()
    if not db_path.exists():
        return []

    repo_root = Path(__file__).resolve().parents[3]
    conn = None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT filename, local_path
            FROM files
            WHERE is_downloaded = 1
            ORDER BY filename
            """
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        if conn is not None:
            conn.close()

    filenames = []
    for row in rows:
        filename = (row["filename"] or "").strip()
        local_path = row["local_path"]
        if not filename or not filename_predicate(filename):
            continue

        if local_path:
            resolved_path = Path(local_path)
            if not resolved_path.is_absolute():
                resolved_path = repo_root / resolved_path
            if not resolved_path.exists():
                continue

        filenames.append(filename)

    # Keep unique exact filenames while preserving sorted query order.
    return list(dict.fromkeys(filenames))
