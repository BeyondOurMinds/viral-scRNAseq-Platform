from pathlib import Path

import pandas as pd


def load_intact_reference(filepath):
    """
    Load the processed IntAct virus-host interaction database.

    Parameters
    ----------
    filepath : str or Path
        Path to the processed IntAct TSV file.

    Returns
    -------
    pd.DataFrame
        IntAct virus-host interaction table.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            f"IntAct reference file not found: {filepath}"
        )

    return pd.read_csv(
        filepath,
        sep="\t",
        dtype=str,
    )

