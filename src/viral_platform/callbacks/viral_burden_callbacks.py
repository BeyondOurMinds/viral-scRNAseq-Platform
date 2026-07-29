from dash import Input, Output, State, dash_table, html, no_update, dcc
import dash_bootstrap_components as dbc
from viral_platform.analysis.viral_burden_associations import calculate_viral_burden_associations, identify_significant_associations
from viral_platform.state.dataset_store import get_working_dataset, get_state_store, set_working_dataset, sync_state_with_dataset
import numpy as np
import pandas as pd
import plotly.express as px
import logging

logger = logging.getLogger(__name__)


def _build_options(values):
    """Build unique dropdown options from an iterable of values."""
    seen = set()
    options = []
    for value in values:
        normalized = str(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        options.append({"label": normalized, "value": normalized})
    return options


def _normalize_column_name(value):
    """Normalize metadata column names for tolerant matching."""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _resolve_column(columns, priority_names, contains_names=None):
    """Resolve a metadata column using exact normalized names then contains checks."""
    contains_names = contains_names or []
    normalized_to_original = {_normalize_column_name(col): col for col in list(columns)}

    for name in priority_names:
        normalized = _normalize_column_name(name)
        if normalized in normalized_to_original:
            return normalized_to_original[normalized]

    for normalized_col, original_col in normalized_to_original.items():
        for token in contains_names:
            normalized_token = _normalize_column_name(token)
            if normalized_token and normalized_token in normalized_col:
                return original_col

    return None


def _resolve_celltype_column(columns):
    """Resolve the most likely cell-type annotation column."""
    return _resolve_column(
        columns,
        priority_names=["cell_type", "celltype", "CellType"],
        contains_names=["celltype", "cell_type", "cell type", "annotation", "cluster"],
    )


def _resolve_condition_column(columns):
    """Resolve the most likely condition/group column."""
    return _resolve_column(
        columns,
        priority_names=["condition", "group", "status", "disease", "treatment"],
        contains_names=["condition", "group", "status", "disease", "treat"],
    )


def _resolve_sample_column(columns, metadata_sample_columns=None):
    """Resolve the most likely sample identifier column."""
    metadata_sample_columns = metadata_sample_columns or []
    normalized_to_original = {_normalize_column_name(col): col for col in list(columns)}

    for candidate in metadata_sample_columns:
        normalized_candidate = _normalize_column_name(candidate)
        if normalized_candidate in normalized_to_original:
            return normalized_to_original[normalized_candidate]

    return _resolve_column(
        columns,
        priority_names=["sampleID", "sample_id", "sample"],
        contains_names=["sampleid", "sample_id", "sample"],
    )


def make_sortable_table(df, table_id):
    """Create a sortable Dash DataTable from a DataFrame."""
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
        page_action="native",
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px", "fontSize": "13px"},
        style_header={"fontWeight": "600"},
    )

def viral_burden_results(adata):
    """Render summary metrics for viral burden analysis as a card/table."""
    infected_cells = (adata.obs['viral_counts'] > 0).sum()
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Viral Burden Analysis Results"),
                dbc.Table(
                    [
                        html.Tbody([
                            html.Tr([html.Td("Cells with Viral Reads"), html.Td(f"{infected_cells}/{adata.n_obs}")]),
                            html.Tr([html.Td("Maximum Viral Counts"), html.Td(f"{adata.obs['viral_counts'].max()}")]),
                            html.Tr([html.Td("Average Viral Counts"), html.Td(f"{adata.obs['viral_counts'].mean():.2f}")]),
                            html.Tr([html.Td("Maximum Viral Burden"), html.Td(f"{adata.obs['viral_burden'].max():.4f}")]),
                            html.Tr([html.Td("Average Viral Burden"), html.Td(f"{adata.obs['viral_burden'].mean():.4f}")]),
                            html.Tr([html.Td("Maximum Viral Burden (%)"), html.Td(f"{adata.obs['viral_burden_percent'].max():.2f}%")]),
                            html.Tr([html.Td("Average Viral Burden (%)"), html.Td(f"{adata.obs['viral_burden_percent'].mean():.2f}%")]),
                        ])
                    ]
                )
            ]
        )
    )


def _build_infection_umap(adata):
    """Create UMAP colored by binary infection status (infected vs non-infected)."""
    if "X_umap" not in adata.obsm:
        return html.Div("UMAP coordinates are not available. Run preprocessing/clustering first.")

    umap_df = pd.DataFrame(adata.obsm["X_umap"], columns=["UMAP1", "UMAP2"], index=adata.obs_names)
    umap_df["infection_status"] = adata.obs["infection_status"].astype(str).values

    # Ensure all non-infected labels map to grey while infected remains green.
    umap_df["infection_status_plot"] = np.where(
        umap_df["infection_status"].str.lower().isin(["infected"]),
        "Infected",
        "Non-infected",
    )

    fig = px.scatter(
        umap_df,
        x="UMAP1",
        y="UMAP2",
        color="infection_status_plot",
        color_discrete_map={"Infected": "green", "Non-infected": "grey"},
        title="Infection UMAP",
        opacity=0.85,
    )
    fig.update_traces(marker={"size": 4})
    fig.update_layout(legend_title_text="")
    return dcc.Graph(figure=fig)


def _build_viral_burden_umap(adata):
    """Create UMAP colored by continuous viral burden values."""
    if "X_umap" not in adata.obsm:
        return html.Div("UMAP coordinates are not available. Run preprocessing/clustering first.")

    umap_df = pd.DataFrame(adata.obsm["X_umap"], columns=["UMAP1", "UMAP2"], index=adata.obs_names)
    umap_df["viral_burden"] = pd.to_numeric(adata.obs["viral_burden"], errors="coerce").fillna(0.0).values

    fig = px.scatter(
        umap_df,
        x="UMAP1",
        y="UMAP2",
        color="viral_burden",
        color_continuous_scale="YlOrRd",
        title="Viral Burden UMAP",
        opacity=0.85,
    )
    fig.update_traces(marker={"size": 4})
    fig.update_coloraxes(colorbar_title="Viral burden")
    return dcc.Graph(figure=fig)


def _build_violin_plots(
    adata,
    celltype_col=None,
    condition_col=None,
    sample_col=None,
    metadata_sample_columns=None,
):
    """Create violin plots of viral burden percent by cell type, condition, and sample."""
    obs = adata.obs.copy()
    obs["viral_burden_percent"] = pd.to_numeric(obs["viral_burden_percent"], errors="coerce").fillna(0.0)

    if celltype_col is None:
        celltype_col = _resolve_celltype_column(obs.columns)
    if condition_col is None:
        condition_col = _resolve_condition_column(obs.columns)
    if sample_col is None:
        sample_col = _resolve_sample_column(obs.columns, metadata_sample_columns=metadata_sample_columns)

    sections = []

    if celltype_col is not None:
        fig_celltype = px.violin(
            obs,
            x=celltype_col,
            y="viral_burden_percent",
            box=True,
            points=False,
            title=f"Viral burden (%) by cell type ({celltype_col})",
        )
        fig_celltype.update_layout(xaxis_tickangle=45)
        sections.append(dcc.Graph(figure=fig_celltype))
    else:
        sections.append(html.Div("No cell type column found for cell type violin plot."))

    if condition_col is not None:
        fig_condition = px.violin(
            obs,
            x=condition_col,
            y="viral_burden_percent",
            box=True,
            points=False,
            title=f"Viral burden (%) by condition ({condition_col})",
        )
        fig_condition.update_layout(xaxis_tickangle=45)
        sections.append(dcc.Graph(figure=fig_condition))
    else:
        sections.append(html.Div("No condition/group column found for condition violin plot."))

    if sample_col is not None:
        fig_sample = px.violin(
            obs,
            x=sample_col,
            y="viral_burden_percent",
            box=True,
            points=False,
            title=f"Viral burden (%) by sample ({sample_col})",
        )
        fig_sample.update_layout(xaxis_tickangle=45)
        sections.append(dcc.Graph(figure=fig_sample))
    else:
        sections.append(html.Div("No sample column found for sample violin plot."))

    return html.Div(sections)


def _build_celltype_infection_fraction_plot(adata, celltype_col=None):
    """Create per-cell-type infection fraction bar chart."""
    obs = adata.obs.copy()
    if celltype_col is None:
        celltype_col = _resolve_celltype_column(obs.columns)
    if celltype_col is None:
        return html.Div("No cell type column found for infection fraction plot.")

    summary = (
        obs.assign(
            infected=obs["infection_status"].astype(str).str.lower().eq("infected").astype(int)
        )
        .groupby(celltype_col, observed=False)
        .agg(total_cells=("infected", "size"), infected_cells=("infected", "sum"))
        .reset_index()
    )

    if summary.empty:
        return html.Div("No cells available for infection fraction plot.")

    summary["infection_fraction"] = summary["infected_cells"] / summary["total_cells"]
    summary = summary.sort_values("infection_fraction", ascending=False)

    fig = px.bar(
        summary,
        x=celltype_col,
        y="infection_fraction",
        color="infection_fraction",
        color_continuous_scale="Greens",
        title="Cell type infection fraction",
        hover_data={
            "infected_cells": True,
            "total_cells": True,
            "infection_fraction": ":.2%",
        },
    )
    fig.update_layout(xaxis_tickangle=45, yaxis_tickformat=".0%")
    return dcc.Graph(figure=fig)

def register_viral_burden_callbacks(app):
    """Register callbacks for viral burden analysis, plotting, and associations."""
    @app.callback(
        Output("viral-burden-advanced-options-collapse", "is_open"),
        Input("viral-burden-advanced-options-button", "n_clicks"),
        State("viral-burden-advanced-options-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_viral_burden_advanced_options(n_clicks, is_open):
        """Toggle visibility of advanced viral burden column selection controls."""
        if not n_clicks:
            return is_open
        return not is_open

    @app.callback(
        Output("viral-burden-celltype-column-dropdown", "options"),
        Output("viral-burden-celltype-column-dropdown", "value"),
        Output("viral-burden-condition-column-dropdown", "options"),
        Output("viral-burden-condition-column-dropdown", "value"),
        Output("viral-burden-sample-column-dropdown", "options"),
        Output("viral-burden-sample-column-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_viral_burden_column_dropdowns(_dataset_version):
        """Populate advanced column dropdowns from dataset metadata with auto-detected defaults."""
        state = get_state_store()
        metadata_info = state.get("metadata_info", {})
        groupable_columns = metadata_info.get("groupable_columns", [])
        metadata_sample_columns = metadata_info.get("sample_columns", [])

        celltype_options = _build_options(groupable_columns)
        condition_options = _build_options(groupable_columns)

        sample_candidates = list(groupable_columns)
        sample_candidates.extend([c for c in metadata_sample_columns if c not in sample_candidates])
        sample_options = _build_options(sample_candidates)

        default_celltype = _resolve_celltype_column(groupable_columns)
        default_condition = _resolve_condition_column(groupable_columns)
        default_sample = _resolve_sample_column(sample_candidates, metadata_sample_columns=metadata_sample_columns)

        if not celltype_options:
            celltype_options = [{"label": "Upload a dataset to select cell type column", "value": ""}]
            default_celltype = ""
        if not condition_options:
            condition_options = [{"label": "Upload a dataset to select condition column", "value": ""}]
            default_condition = ""
        if not sample_options:
            sample_options = [{"label": "Upload a dataset to select sample column", "value": ""}]
            default_sample = ""

        if default_celltype not in {opt["value"] for opt in celltype_options}:
            default_celltype = celltype_options[0]["value"] if celltype_options else ""
        if default_condition not in {opt["value"] for opt in condition_options}:
            default_condition = condition_options[0]["value"] if condition_options else ""
        if default_sample not in {opt["value"] for opt in sample_options}:
            default_sample = sample_options[0]["value"] if sample_options else ""

        return (
            celltype_options,
            default_celltype,
            condition_options,
            default_condition,
            sample_options,
            default_sample,
        )

    @app.callback(
        Output("viral-burden-loading-signal", "children"),
        Output("viral-burden-results-container", "children"),
        Output("viral-burden-infection-umap-container", "children"),
        Output("viral-burden-umap-container", "children"),
        Output("viral-burden-violin-container", "children"),
        Output("viral-burden-celltype-fraction-container", "children"),
        Output("viral-burden-associations-container", "hidden"),
        Input("run-viral-burden-analysis-button", "n_clicks"),
        State("viral-burden-celltype-column-dropdown", "value"),
        State("viral-burden-condition-column-dropdown", "value"),
        State("viral-burden-sample-column-dropdown", "value"),
        prevent_initial_call=True,
    )
    def run_viral_burden_analysis(
        n_clicks,
        selected_celltype_column,
        selected_condition_column,
        selected_sample_column,
    ):
        """
        Calculate viral burden for each cell and render tabbed outputs.

        Parameters
        ----------
        adata : AnnData
            Dataset containing expression matrix.

        detected_features : list
            List of viral feature names returned by the viral
            detection module.

        Returns
        -------
        tuple
            Loading signal, rendered results/plots, and association-section visibility.
        """
        if n_clicks is None or n_clicks == 0:
            return (
                no_update,
                "No viral burden results yet. Run the analysis to see results here.",
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        
        history = get_state_store()
        adata = get_working_dataset()
        if adata is None:
            message = "No dataset available for viral burden analysis."
            return "done", message, message, message, message, message, True
        
        features = history.get("viral_detection", {}).get("viral_features", "")
        metadata_info = history.get("metadata_info", {})
        metadata_sample_columns = metadata_info.get("sample_columns", [])
        history = None # remove local history object to free memory
        if not features:
            message = "No viral features detected. Please run viral gene detection first."
            return "done", message, message, message, message, message, True

        if isinstance(features, str):
            features = [f.strip() for f in features.split(",") if f.strip()]
        else:
            features = [f for f in features if f]

        if not features:
            message = "No valid viral features detected. Please run viral gene detection first."
            return "done", message, message, message, message, message, True
        
        # grabbing raw counts matrix from adata.layers["counts"]
        matrix = (adata.layers["counts"])

        # extracting only viral features
        viral_matrix = matrix[:, adata.var_names.isin(features)].copy()

        # Sum viral counts per cell
        viral_counts = viral_matrix.sum(axis=1)
        if hasattr(viral_counts, "A1"):  # Check if it's a sparse matrix
            viral_counts = viral_counts.A1  # Convert to 1D array
        else:
            viral_counts = np.array(viral_counts).flatten()  # Ensure it's a 1D array

        
        # store raw viral counts in adata.obs
        adata.obs["viral_counts"] = viral_counts


        # calculate viral burden
        adata.obs["viral_burden"] = (
            adata.obs["viral_counts"] / adata.obs["total_counts"]
        )

        # percentage burden
        adata.obs["viral_burden_percent"] = adata.obs["viral_burden"] * 100

        #infection status
        adata.obs["infection_status"] = np.where(
            adata.obs["viral_counts"] > 0, "Infected", "Bystander" # eventually change this to accept a threshold from the user or default to 0
        )

        # log1p transformation of viral counts
        adata.obs["log1p_viral_counts"] = np.log1p(adata.obs["viral_counts"])

        # update the working dataset in the state store
        set_working_dataset(adata)
        sync_state_with_dataset(adata)


        logger.info("Viral burden analysis completed successfully.")

        celltype_col = (
            selected_celltype_column
            if selected_celltype_column and selected_celltype_column in adata.obs.columns
            else _resolve_celltype_column(adata.obs.columns)
        )
        condition_col = (
            selected_condition_column
            if selected_condition_column and selected_condition_column in adata.obs.columns
            else _resolve_condition_column(adata.obs.columns)
        )
        sample_col = (
            selected_sample_column
            if selected_sample_column and selected_sample_column in adata.obs.columns
            else _resolve_sample_column(
                adata.obs.columns,
                metadata_sample_columns=metadata_sample_columns,
            )
        )

        infection_umap = _build_infection_umap(adata)
        viral_burden_umap = _build_viral_burden_umap(adata)
        violin_plots = _build_violin_plots(
            adata,
            celltype_col=celltype_col,
            condition_col=condition_col,
            sample_col=sample_col,
            metadata_sample_columns=metadata_sample_columns,
        )
        celltype_fraction_plot = _build_celltype_infection_fraction_plot(
            adata,
            celltype_col=celltype_col,
        )

        return (
            "done",
            viral_burden_results(adata),
            infection_umap,
            viral_burden_umap,
            violin_plots,
            celltype_fraction_plot,
            False,
        )
    
    @app.callback(
        Output("viral-burden-associations-loading-signal", "children"),
        Output("viral-burden-associations-results-container", "children"),
        Output("viral-burden-associations-significant-results-container", "children"),
        Input("run-viral-burden-association-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def run_viral_burden_associations(n_clicks):
        """Run viral burden association analysis and render full/significant result tables."""
        if n_clicks is None or n_clicks == 0:
            return no_update, "No viral burden association results yet. Run the analysis to see results here.", ""
        
        adata = get_working_dataset()
        if adata is None:
            return no_update, "No dataset available for viral burden association analysis.", ""
        
        features = get_state_store().get("viral_detection", {}).get("viral_features", "")
        if not features:
            return no_update, "No viral features detected. Please run viral gene detection first.", ""

        if isinstance(features, str):
            features = [f.strip() for f in features.split(",") if f.strip()]
        else:
            features = [f for f in features if f]

        if not features:
            return no_update, "No valid viral features detected. Please run viral gene detection first.", ""
        
        try:
            associations_df = calculate_viral_burden_associations(features)
            logger.info("Viral burden association analysis completed successfully.")
            significant_associations_df = identify_significant_associations(associations_df)
            logger.info("Significant viral burden associations identified successfully.")
            return (
                "done",
                make_sortable_table(associations_df, "viral-burden-associations-table"),
                make_sortable_table(significant_associations_df, "viral-burden-significant-associations-table"),
            )
        except Exception as e:
            logger.exception("Failed to calculate viral burden associations: %s", str(e))
            return no_update, f"Failed to calculate viral burden associations: {str(e)}", ""