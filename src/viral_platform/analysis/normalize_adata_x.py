"""Utilities for checking and normalizing `adata.X`.

This module provides a small helper that inspects `adata.X` to determine whether
it still appears to contain raw counts. If so, it normalizes total counts and
applies `log1p` before returning the AnnData object.
"""

import logging

import scanpy as sc

from viral_platform.analysis.find_raw_counts import looks_like_raw_counts


logger = logging.getLogger(__name__)


def ensure_log_normalized_x(adata, target_sum=1e4, inplace=True):
	"""Ensure that `adata.X` is log-normalized.

	The helper inspects only `adata.X`. If the matrix looks like raw counts,
	it applies `sc.pp.normalize_total` followed by `sc.pp.log1p`.

	Parameters
	----------
	adata : AnnData
		Input AnnData object.
	target_sum : float, optional
		Library-size target used for normalization, by default 1e4.
	inplace : bool, optional
		If True, modify the supplied AnnData object in place. If False, work on a
		copy and return the normalized copy.

	Returns
	-------
	AnnData
		The original AnnData object or a normalized copy.
	"""
	if adata is None:
		raise ValueError("adata cannot be None.")

	working = adata if inplace else adata.copy()
	assessment = looks_like_raw_counts(working.X)

	if assessment["looks_like_counts"]:
		logger.info(
			"adata.X appears to contain raw counts (%s, confidence=%s). Applying normalize_total + log1p.",
			assessment["reason"],
			assessment["confidence"],
		)
		sc.pp.normalize_total(working, target_sum=target_sum)
		sc.pp.log1p(working)
	else:
		logger.info(
			"adata.X does not appear to contain raw counts (%s, confidence=%s). Leaving matrix unchanged.",
			assessment["reason"],
			assessment["confidence"],
		)

	return working