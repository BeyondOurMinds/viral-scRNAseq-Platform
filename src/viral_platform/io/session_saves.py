import io
import json
import pickle
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scanpy as sc

from viral_platform.state.dataset_store import (
    get_state_snapshot,
    get_state_store,
    get_working_dataset,
    restore_state_snapshot,
    set_dataset,
    set_results_cache,
    set_working_dataset,
    sync_state_with_dataset,
)
from viral_platform.utils.logging_config import get_captured_logs_text

SAVE_FILENAME = "session.h5ad"
RESULTS_CACHE_FILENAME = "results_cache.pkl"
STATE_UNS_KEY = "viral_platform_state_history"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAVES_ROOT = PROJECT_ROOT / "saves"

_INVALID_PATH_CHARS = re.compile(r'[<>:"/\\|?*]+')


def ensure_saves_dir():
    SAVES_ROOT.mkdir(parents=True, exist_ok=True)
    return SAVES_ROOT


def get_saves_dir():
    return ensure_saves_dir()


def normalize_save_name(name):
    cleaned = (name or "").strip()
    cleaned = _INVALID_PATH_CHARS.sub("_", cleaned)
    cleaned = "_".join(cleaned.split())
    return cleaned.strip("._")


def _to_h5ad_compatible(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, np.ndarray):
        return [_to_h5ad_compatible(item) for item in value.tolist()]

    if isinstance(value, pd.DataFrame):
        return {
            "__type__": "dataframe",
            "columns": [str(col) for col in value.columns],
            "records": [_to_h5ad_compatible(row) for row in value.to_dict(orient="records")],
        }

    if isinstance(value, pd.Series):
        return {
            "__type__": "series",
            "name": str(value.name),
            "values": [_to_h5ad_compatible(item) for item in value.tolist()],
        }

    if isinstance(value, dict):
        return {str(k): _to_h5ad_compatible(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_h5ad_compatible(item) for item in value]

    return {
        "__type__": "repr",
        "value": repr(value),
    }


def _component_to_jsonable(value):
    """Convert cached Dash components into plain Python JSON-compatible structures."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, np.ndarray):
        return [_component_to_jsonable(item) for item in value.tolist()]

    if isinstance(value, pd.DataFrame):
        return {
            "__type__": "dataframe",
            "columns": [str(col) for col in value.columns],
            "records": [_component_to_jsonable(row) for row in value.to_dict(orient="records")],
        }

    if isinstance(value, pd.Series):
        return [_component_to_jsonable(item) for item in value.tolist()]

    if hasattr(value, "to_plotly_json"):
        try:
            value = value.to_plotly_json()
        except Exception:
            return repr(value)

    if isinstance(value, dict):
        return {str(k): _component_to_jsonable(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_component_to_jsonable(item) for item in value]

    return repr(value)


def _make_results_cache_portable(results_cache):
    portable = {}
    for key, value in (results_cache or {}).items():
        portable[str(key)] = _component_to_jsonable(value)
    return portable


def _write_h5ad_with_nullable_strings(adata, path):
    """Opt-in to AnnData nullable-string writing for cross-panel session saves."""
    setting_name = "allow_write_nullable_strings"
    if not hasattr(ad.settings, setting_name):
        adata.write_h5ad(str(path))
        return

    prior = getattr(ad.settings, setting_name)
    try:
        setattr(ad.settings, setting_name, True)
        adata.write_h5ad(str(path))
    finally:
        setattr(ad.settings, setting_name, prior)


def _serialize_history_for_uns():
    snapshot = get_state_snapshot(include_results_cache=False)
    # Persist as JSON text to avoid h5ad nested-object coercion issues.
    return json.dumps(_to_h5ad_compatible(snapshot), ensure_ascii=False)


def _deserialize_history_from_uns(stored_value):
    if isinstance(stored_value, dict):
        # Backward compatibility for earlier saves that stored a mapping directly.
        return stored_value

    if isinstance(stored_value, str):
        try:
            loaded = json.loads(stored_value)
            return loaded if isinstance(loaded, dict) else {}
        except Exception:
            return {}

    return {}


def _load_results_cache_from_disk(save_dir):
    cache_path = save_dir / RESULTS_CACHE_FILENAME
    if not cache_path.exists():
        return {}, None

    try:
        with cache_path.open("rb") as handle:
            loaded = pickle.load(handle)
        if isinstance(loaded, dict):
            return loaded, None
        return {}, "Results cache file was not a dictionary and was skipped."
    except Exception as exc:
        return {}, f"Could not load results cache: {exc}"


def list_saved_sessions():
    saves_dir = ensure_saves_dir()
    sessions = []

    for child in saves_dir.iterdir():
        if not child.is_dir():
            continue

        session_file = child / SAVE_FILENAME
        if not session_file.exists():
            continue

        sessions.append({
            "name": child.name,
            "path": child,
            "mtime": session_file.stat().st_mtime,
        })

    sessions.sort(key=lambda item: item["mtime"], reverse=True)
    return sessions


def save_current_session(save_name):
    name = normalize_save_name(save_name)
    if not name:
        raise ValueError("Please enter a save name for the folder.")

    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No working dataset is loaded. Upload data before saving.")

    saves_dir = ensure_saves_dir()
    save_dir = saves_dir / name
    save_dir.mkdir(parents=True, exist_ok=True)

    session_path = save_dir / SAVE_FILENAME
    warnings = []

    adata_to_save = adata.copy()
    adata_to_save.uns[STATE_UNS_KEY] = _serialize_history_for_uns()
    adata_to_save.uns["viral_platform_saved_at_utc"] = datetime.now(timezone.utc).isoformat()

    _write_h5ad_with_nullable_strings(adata_to_save, session_path)

    cache_path = save_dir / RESULTS_CACHE_FILENAME
    try:
        with cache_path.open("wb") as handle:
            pickle.dump(
                _make_results_cache_portable(get_state_store().get("results_cache", {})),
                handle,
            )
    except Exception as exc:
        warnings.append(f"Saved dataset but could not persist results cache: {exc}")

    return {
        "name": name,
        "folder": save_dir,
        "session_file": session_path,
        "warnings": warnings,
    }


def load_saved_session(save_name):
    name = normalize_save_name(save_name)
    if not name:
        raise ValueError("Select a save folder to load.")

    save_dir = ensure_saves_dir() / name
    session_path = save_dir / SAVE_FILENAME
    if not session_path.exists():
        raise FileNotFoundError(f"No saved session found at {session_path}")

    adata = sc.read_h5ad(str(session_path))
    stored_snapshot = _deserialize_history_from_uns(adata.uns.get(STATE_UNS_KEY, {}))

    set_dataset(adata.copy())
    set_working_dataset(adata)

    restore_state_snapshot(stored_snapshot, include_results_cache=False)

    results_cache, cache_warning = _load_results_cache_from_disk(save_dir)
    set_results_cache(results_cache)
    sync_state_with_dataset(adata)

    warnings = []
    if cache_warning:
        warnings.append(cache_warning)

    return {
        "name": name,
        "cells": int(adata.n_obs),
        "genes": int(adata.n_vars),
        "warnings": warnings,
    }


def _walk_cached_nodes(node):
    if node is None:
        return

    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk_cached_nodes(item)
        return

    if hasattr(node, "to_plotly_json"):
        try:
            node = node.to_plotly_json()
        except Exception:
            return

    if isinstance(node, dict):
        if "type" in node and "props" in node and isinstance(node.get("props"), dict):
            props = node.get("props") or {}

            figure_payload = props.get("figure")
            if isinstance(figure_payload, go.Figure):
                yield ("figure", figure_payload)
            elif isinstance(figure_payload, dict):
                yield ("figure", figure_payload)

            table_columns = props.get("columns")
            table_data = props.get("data")
            if isinstance(table_columns, list) and isinstance(table_data, list):
                yield (
                    "table",
                    {
                        "columns": table_columns,
                        "data": table_data,
                    },
                )

            for prop_name, prop_value in props.items():
                if prop_name in {"figure", "columns", "data"}:
                    continue
                yield from _walk_cached_nodes(prop_value)
            return

        if isinstance(node.get("data"), list) and isinstance(node.get("layout"), dict):
            yield ("figure", node)
            return

        if isinstance(node, go.Figure):
            yield ("figure", node)
            return

        for value in node.values():
            yield from _walk_cached_nodes(value)


def _safe_component_name(text, fallback):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text or "")
    cleaned = cleaned.strip("._")
    return cleaned or fallback


def _extract_tables_and_figures(results_cache):
    tables = []
    figures = []

    for cache_key, component in (results_cache or {}).items():
        table_index = 1
        figure_index = 1

        for item_type, payload in _walk_cached_nodes(component):
            if item_type == "table":
                columns = payload.get("columns") or []
                data = payload.get("data") or []
                if not isinstance(data, list):
                    continue

                table_name = _safe_component_name(cache_key, "table")
                table_id = f"{table_name}_table_{table_index}"
                table_index += 1

                df = pd.DataFrame(data)
                column_ids = [col.get("id") for col in columns if isinstance(col, dict) and col.get("id")]
                if column_ids and all(col in df.columns for col in column_ids):
                    df = df[column_ids]

                tables.append((table_id, df))

            if item_type == "figure":
                fig_name = _safe_component_name(cache_key, "figure")
                figure_id = f"{fig_name}_figure_{figure_index}"
                figure_index += 1
                figures.append((figure_id, payload))

    return tables, figures


def _prepare_figure_for_export(figure_like):
    """Return a Plotly figure tuned for static export readability."""
    fig = figure_like if isinstance(figure_like, go.Figure) else go.Figure(figure_like)
    fig = go.Figure(fig)

    legend = fig.layout.legend
    if legend and getattr(legend, "orientation", None) == "h":
        current_margin = fig.layout.margin or {}
        bottom_margin = max(int(getattr(current_margin, "b", 0) or 0), 220)
        fig.update_layout(
            margin=dict(
                l=int(getattr(current_margin, "l", 0) or 0),
                r=int(getattr(current_margin, "r", 0) or 0),
                t=int(getattr(current_margin, "t", 60) or 60),
                b=bottom_margin,
            ),
            width=max(int(getattr(fig.layout, "width", 0) or 0), 1600),
            height=max(int(getattr(fig.layout, "height", 0) or 0), 900),
        )

    return fig


def _build_log_text(include_metadata, include_tables_figures):
    adata = get_working_dataset()
    captured_logs = get_captured_logs_text().strip()

    lines = [
        "viral_platform logger export",
        f"created_utc: {datetime.now(timezone.utc).isoformat()}",
        f"cells: {int(adata.n_obs) if adata is not None else 0}",
        f"genes: {int(adata.n_vars) if adata is not None else 0}",
        f"included_metadata_csv: {bool(include_metadata)}",
        f"included_tables_figures: {bool(include_tables_figures)}",
        "",
        "captured_logger_output:",
        captured_logs if captured_logs else "<no logger messages captured>",
    ]
    return "\n".join(lines)


def create_optional_exports_bundle(include_metadata=False, include_tables_figures=False, include_log=False):
    if not any([include_metadata, include_tables_figures, include_log]):
        raise ValueError("Select at least one optional export item.")

    adata = get_working_dataset()
    if adata is None:
        raise ValueError("No working dataset is loaded. Upload data before exporting.")

    file_payloads = {}
    notes = []

    if include_metadata:
        metadata_csv = adata.obs.copy().to_csv(index=True)
        file_payloads["metadata/metadata.csv"] = metadata_csv.encode("utf-8")

    if include_tables_figures:
        tables, figures = _extract_tables_and_figures(get_state_store().get("results_cache", {}))

        for table_name, table_df in tables:
            file_payloads[f"tables/{table_name}.csv"] = table_df.to_csv(index=False).encode("utf-8")

        for figure_name, figure_dict in figures:
            try:
                export_fig = _prepare_figure_for_export(figure_dict)
                svg_bytes = export_fig.to_image(format="svg")
                file_payloads[f"figures/{figure_name}.svg"] = svg_bytes
            except Exception as exc:
                notes.append(f"Could not export figure '{figure_name}' as SVG: {exc}")

        notes.append(f"Exported {len(tables)} table(s).")
        notes.append(f"Exported {len([name for name in file_payloads if name.startswith('figures/')])} figure(s) as SVG.")

    if include_log:
        log_text = _build_log_text(include_metadata, include_tables_figures)
        file_payloads["logs/session_export.log"] = log_text.encode("utf-8")

    if not file_payloads:
        raise ValueError("No optional export files were generated.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative_path, payload in file_payloads.items():
            archive.writestr(relative_path, payload)

    zip_buffer.seek(0)
    zip_name = f"viral_platform_optional_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return zip_name, zip_buffer.getvalue(), notes
