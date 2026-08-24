import numpy as np
from scipy.sparse import issparse


def looks_like_raw_counts(matrix):
    """
    Determine whether a matrix appears to contain raw UMI counts.

    Parameters
    ----------
    matrix : numpy.ndarray or scipy.sparse matrix

    Returns
    -------
    dict
        {
            "looks_like_counts": bool,
            "confidence": "high" | "medium" | "low",
            "reason": str,
            "summary": {
                "min": float,
                "max": float,
                "mean": float,
                "integer_fraction": float,
                "negative_fraction": float
            }
        }
    """

    if matrix is None:
        return {
            "looks_like_counts": False,
            "confidence": "low",
            "reason": "Matrix is None.",
            "summary": None
        }

    if issparse(matrix):
        data = matrix.data
    else:
        data = np.asarray(matrix).ravel()

    if data.size == 0:
        return {
            "looks_like_counts": False,
            "confidence": "low",
            "reason": "Matrix contains no values.",
            "summary": None
        }

    minimum = float(np.min(data))
    maximum = float(np.max(data))
    mean = float(np.mean(data))

    negative_fraction = float(np.mean(data < 0))
    integer_fraction = float(
        np.mean(np.isclose(data, np.round(data)))
    )

    summary = {
        "min": minimum,
        "max": maximum,
        "mean": mean,
        "integer_fraction": integer_fraction,
        "negative_fraction": negative_fraction,
    }

    # Negative values immediately rule out raw counts
    if negative_fraction > 0:
        return {
            "looks_like_counts": False,
            "confidence": "high",
            "reason": "Matrix contains negative values.",
            "summary": summary,
        }

    # Almost all values should be integer-like
    if integer_fraction >= 0.999:
        return {
            "looks_like_counts": True,
            "confidence": "high",
            "reason": "Values are non-negative and almost entirely integers.",
            "summary": summary,
        }

    if integer_fraction >= 0.95:
        return {
            "looks_like_counts": True,
            "confidence": "medium",
            "reason": "Most values are integer-like.",
            "summary": summary,
        }

    return {
        "looks_like_counts": False,
        "confidence": "high",
        "reason": "Large proportion of non-integer values.",
        "summary": summary,
    }


def find_raw_count_matrix(adata):
    """
    Find the most likely raw count matrix in an AnnData object.

    Search order:

        1. layers["counts"]
        2. layers["raw"]
        3. layers["umi"]
        4. adata.raw.X
        5. adata.X

    Returns
    -------
    dict
        {
            "found": bool,
            "location": str | None,
            "assessment": dict
        }
    """

    candidates = []

    # Common layer names
    for layer in ("counts", "raw", "umi"):

        if layer in adata.layers:

            candidates.append(
                (
                    f'layers["{layer}"]',
                    adata.layers[layer]
                )
            )

    # adata.raw
    if adata.raw is not None:
        candidates.append(
            (
                "adata.raw.X",
                adata.raw.X
            )
        )

    # Current matrix
    candidates.append(
        (
            "adata.X",
            adata.X
        )
    )

    # Test each candidate
    for location, matrix in candidates:

        assessment = looks_like_raw_counts(matrix)

        if assessment["looks_like_counts"]:

            return {
                "found": True,
                "location": location,
                "assessment": assessment,
            }

    return {
        "found": False,
        "location": None,
        "assessment": {
            "looks_like_counts": False,
            "confidence": "low",
            "reason": "No candidate matrix appears to contain raw counts.",
            "summary": None,
        },
    }

def get_raw_count_matrix(adata, location):
    if location == "adata.X":
        return adata.X

    if location == "adata.raw.X":
        return adata.raw.X

    if location.startswith('layers["'):
        layer = location[8:-2]
        return adata.layers[layer]