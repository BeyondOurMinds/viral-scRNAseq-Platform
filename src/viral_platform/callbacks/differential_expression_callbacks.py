import logging

import numpy as np
import pandas as pd
import plotly.express as px
from scipy.sparse import issparse

from dash import Input, Output, State, html, dash_table, dcc
import dash_bootstrap_components as dbc

from viral_platform.state.dataset_store import (
    get_state_store,
    get_working_dataset,
    reset_state_store,
)
from viral_platform.analysis.pseudobulk import subset_cells
from viral_platform.analysis.differential_expression import run_differential_expression
from viral_platform.utils.sample_column_utils import resolve_sample_column
from viral_platform.utils.reference_file_utils import (
    read_downloaded_reference_filenames,
)

logger = logging.getLogger(__name__)

MAX_DROPDOWN_CATEGORY_VALUES = 500
DE_REFERENCE_SUFFIXES = ("_degs.json", "_degs_top.json", "_gene_heatmap.json")


def _read_downloaded_de_reference_filenames():
    return read_downloaded_reference_filenames(
        lambda filename: filename.lower().endswith(DE_REFERENCE_SUFFIXES)
    )


def _build_options(values):
    """Normalize iterable values into unique Dash dropdown option dictionaries."""
    seen = set()
    options = []
    for value in values:
        normalized = str(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        options.append({"label": normalized, "value": normalized})
    return options


def _guess_cell_type_columns(groupable_columns):
    """Find likely cell-type metadata columns from available groupable columns."""
    matches = []
    for col in groupable_columns:
        lowered = str(col).lower()
        if "cell_type" in lowered or "celltype" in lowered or "cell type" in lowered:
            matches.append(col)
    return matches


def _normalize_de_result_gene_column(df, celltype_label):
    """Normalize DE result gene identifier column names to a single 'gene' field."""
    if "gene" in df.columns:
        return df

    rename_candidates = ("var_names", "index", "gene_name", "names")
    for candidate in rename_candidates:
        if candidate in df.columns:
            print(
                f"[DE heatmap debug] celltype={celltype_label} using '{candidate}' as gene column"
            )
            return df.rename(columns={candidate: "gene"})

    print(
        f"[DE heatmap debug] celltype={celltype_label} no recognizable gene column; "
        f"available={list(df.columns)}"
    )
    return df


def register_differential_expression_callbacks(app):
    """Register callbacks that keep DE dropdown options synchronized with dataset metadata/state."""

    @app.callback(
        Output("de-reference-file-radio", "options"),
        Output("de-reference-file-radio", "value"),
        Input("scmovir-refresh-token", "data"),
        prevent_initial_call=False,
    )
    def populate_de_reference_files(_refresh_token):
        filenames = _read_downloaded_de_reference_filenames()
        if not filenames:
            return (
                [{"label": "No downloaded DE reference files found.", "value": ""}],
                "",
            )

        options = [{"label": name, "value": name} for name in filenames]
        return options, options[0]["value"]

    @app.callback(
        Output("grouping-variable-dropdown", "options"),
        Output("grouping-variable-dropdown", "value"),
        Output("ccc-grouping-dropdown", "options"),
        Output("ccc-grouping-dropdown", "value"),
        Output("celltype-variable-dropdown", "options"),
        Output("celltype-variable-dropdown", "value"),
        Output("celltype-dropdown", "options"),
        Output("celltype-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_metadata_driven_dropdowns(_dataset_version):
        """Populate grouping-variable and celltype dropdowns from history metadata_info."""
        if _dataset_version is None:
            # Browser was refreshed or is a new session with no upload — clear any
            # stale server-side state left over from a previous upload in this process.
            reset_state_store()

        state = get_state_store()
        metadata_info = state.get("metadata_info", {})

        groupable_columns = metadata_info.get("groupable_columns", [])
        grouping_options = _build_options(groupable_columns)
        grouping_value = grouping_options[0]["value"] if grouping_options else None

        # Allow any groupable metadata column to be used as the cell-type field.
        # Some datasets use non-standard names for cell type annotations.
        celltype_variable_options = _build_options(groupable_columns)
        likely_celltype_columns = _guess_cell_type_columns(groupable_columns)
        if likely_celltype_columns:
            celltype_variable_value = str(likely_celltype_columns[0])
        else:
            celltype_variable_value = (
                celltype_variable_options[0]["value"]
                if celltype_variable_options
                else None
            )

        # Values for this dropdown are populated by the celltype-column callback.
        celltype_options = [
            {"label": "Select a cell type column to load cell types", "value": ""}
        ]
        celltype_value = ""

        if not grouping_options:
            grouping_options = [
                {"label": "Upload a dataset to select grouping variable", "value": ""}
            ]
            grouping_value = ""

        if not celltype_variable_options:
            celltype_variable_options = [
                {"label": "Upload a dataset to select cell type column", "value": ""}
            ]
            celltype_variable_value = ""

        logger.info(
            "Populated DE metadata dropdowns with %s grouping columns and %s cell-type columns.",
            len(grouping_options),
            len(celltype_variable_options),
        )

        ccc_grouping_options = grouping_options
        ccc_grouping_value = grouping_value

        return (
            grouping_options,
            grouping_value,
            ccc_grouping_options,
            ccc_grouping_value,
            celltype_variable_options,
            celltype_variable_value,
            celltype_options,
            celltype_value,
        )

    @app.callback(
        Output("celltype-dropdown", "options", allow_duplicate=True),
        Output("celltype-dropdown", "value", allow_duplicate=True),
        Input("celltype-variable-dropdown", "value"),
        Input("active-dataset-version", "data"),
        prevent_initial_call=True,
    )
    def populate_celltype_values(celltype_column, _dataset_version):
        """Populate cell-type values based on the selected cell-type metadata column."""
        adata = get_working_dataset()
        if adata is None:
            return (
                [{"label": "Upload a dataset to select cell type", "value": ""}],
                "",
            )

        if not celltype_column or celltype_column not in adata.obs.columns:
            return (
                [
                    {
                        "label": "Select a cell type column to load cell types",
                        "value": "",
                    }
                ],
                "",
            )

        unique_values = (
            adata.obs[celltype_column].dropna().astype(str).unique().tolist()
        )
        unique_values = [v for v in unique_values if v.strip()]

        if len(unique_values) > MAX_DROPDOWN_CATEGORY_VALUES:
            logger.warning(
                "Skipping DE cell-type option expansion for '%s': %d values exceed max %d.",
                celltype_column,
                len(unique_values),
                MAX_DROPDOWN_CATEGORY_VALUES,
            )
            return (
                [
                    {
                        "label": (
                            f"Selected column has {len(unique_values)} distinct values. "
                            "Choose a lower-cardinality annotation column."
                        ),
                        "value": "",
                    }
                ],
                "",
            )

        ordered_values = ["All Cells"] + [
            v for v in unique_values if v.lower() != "all cells"
        ]
        options = _build_options(ordered_values)

        if not options:
            return (
                [{"label": "No cell types found for selected column", "value": ""}],
                "",
            )

        logger.info(
            "Populated DE cell-type dropdown for '%s' with %s values.",
            celltype_column,
            len(options),
        )
        return options, options[0]["value"]

    @app.callback(
        Output("group1-dropdown", "options"),
        Output("group1-dropdown", "value"),
        Output("group2-dropdown", "options"),
        Output("group2-dropdown", "value"),
        Input("grouping-variable-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_group_comparison_dropdowns(grouping_column, _dataset_version):
        """Populate group1/group2 dropdowns with unique values from the selected grouping column."""
        adata = get_working_dataset()
        if adata is None:
            return (
                [
                    {
                        "label": "Select a grouping variable to select group 1",
                        "value": "",
                    }
                ],
                "",
                [
                    {
                        "label": "Select a grouping variable to select group 2",
                        "value": "",
                    }
                ],
                "",
            )

        if not grouping_column or grouping_column not in adata.obs.columns:
            return (
                [
                    {
                        "label": "Select a grouping variable to select group 1",
                        "value": "",
                    }
                ],
                "",
                [
                    {
                        "label": "Select a grouping variable to select group 2",
                        "value": "",
                    }
                ],
                "",
            )

        unique_values = (
            adata.obs[grouping_column].dropna().astype(str).unique().tolist()
        )
        unique_values = [v for v in unique_values if v.strip()]

        if len(unique_values) > MAX_DROPDOWN_CATEGORY_VALUES:
            logger.warning(
                "Skipping DE group option expansion for '%s': %d values exceed max %d.",
                grouping_column,
                len(unique_values),
                MAX_DROPDOWN_CATEGORY_VALUES,
            )
            warning_option = [
                {
                    "label": (
                        f"Selected column has {len(unique_values)} distinct values. "
                        "Choose a lower-cardinality grouping column."
                    ),
                    "value": "",
                }
            ]
            return warning_option, "", warning_option, ""

        options = _build_options(unique_values)

        if not options:
            return (
                [{"label": "No groups found for selected variable", "value": ""}],
                "",
                [{"label": "No groups found for selected variable", "value": ""}],
                "",
            )

        group1_value = options[0]["value"]
        group2_value = options[1]["value"] if len(options) > 1 else options[0]["value"]

        logger.info(
            "Populated DE group dropdowns for '%s' with %s group values.",
            grouping_column,
            len(options),
        )
        return options, group1_value, options, group2_value

    @app.callback(
        Output("differential-expression-loading-signal", "children"),
        Output("pseudobulk-container", "children"),
        Output("de-table-container", "children"),
        Output("volcano-plot-container", "children"),
        Output("de-heatmap-container", "children"),
        Input("run-differential-expression-analysis-button", "n_clicks"),
        State("grouping-variable-dropdown", "value"),
        State("group1-dropdown", "value"),
        State("group2-dropdown", "value"),
        State("celltype-variable-dropdown", "value"),
        State("celltype-dropdown", "value"),
    )
    def run_DE_analysis(n_clicks, grouping, group1, group2, celltype_column, celltype):
        """Run differential expression analysis when the button is clicked."""
        if n_clicks == 0:
            return (
                "",
                "Upload a dataset to run differential expression analysis.",
                "",
                "",
                "",
            )

        adata_for_values = get_working_dataset()
        if adata_for_values is None:
            return (
                "Upload a dataset to run differential expression analysis.",
                "",
                "",
                "",
                "",
            )

        if not celltype_column or celltype_column not in adata_for_values.obs.columns:
            return (
                "Select a valid cell type column before running differential expression.",
                "",
                "",
                "",
                "",
            )

        # Build the analysis target list: a single selected cell type, or every
        # value in the selected cell-type column when user selects "All Cells".
        if celltype != "All Cells":
            target_celltypes = [celltype]
        else:
            target_celltypes = [
                ct
                for ct in adata_for_values.obs[celltype_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
                if str(ct).strip().lower() != "all cells" and str(ct).strip() != ""
            ]

        if not target_celltypes:
            return (
                "No cell types available for differential expression analysis.",
                "",
                "",
                "",
                "",
            )

        # Keep unique order in case metadata_info has duplicates.
        target_celltypes = list(dict.fromkeys(target_celltypes))

        state = get_state_store()
        metadata_info = state.get("metadata_info", {})
        metadata_sample_columns = metadata_info.get("sample_columns", [])

        pseudobulk_items = []
        de_items = []
        volcano_items = []
        heatmap_items = []
        completed = 0

        # Run the full DE pipeline independently for each target cell type so
        # each section can be rendered as its own collapsible output.
        for ct in target_celltypes:
            print(f"Running DE for {ct}")
            adata = subset_cells(grouping, group1, group2, ct, celltype_column)
            if adata is None:
                logger.warning(
                    "Skipping DE for cell type '%s' due to missing/invalid subset.", ct
                )
                continue

            adata, results = run_differential_expression(
                adata, grouping, group1, group2, ct
            )
            if adata is None or not hasattr(adata, "obs"):
                logger.warning(
                    "Skipping DE for cell type '%s' due to failed DE analysis.", ct
                )
                continue

            completed += 1

            if grouping in adata.obs.columns:
                sample_id_col = resolve_sample_column(
                    adata.obs.columns,
                    metadata_sample_columns=metadata_sample_columns,
                    obs_df=adata.obs,
                )
                if sample_id_col is not None:
                    group1_n = adata.obs[adata.obs[grouping] == group1][
                        sample_id_col
                    ].nunique()
                    group2_n = adata.obs[adata.obs[grouping] == group2][
                        sample_id_col
                    ].nunique()
                else:
                    group1_n = "N/A"
                    group2_n = "N/A"
            else:
                group1_n = "N/A"
                group2_n = "N/A"

            median_cells = (
                int(adata.obs["psbulk_cells"].median())
                if "psbulk_cells" in adata.obs.columns
                else "N/A"
            )
            median_counts = (
                int(adata.obs["psbulk_counts"].median())
                if "psbulk_counts" in adata.obs.columns
                else "N/A"
            )
            min_cells = (
                int(adata.obs["psbulk_cells"].min())
                if "psbulk_cells" in adata.obs.columns
                else "N/A"
            )
            min_counts = (
                int(adata.obs["psbulk_counts"].min())
                if "psbulk_counts" in adata.obs.columns
                else "N/A"
            )

            # Per-celltype pseudobulk summary table.
            pseudobulk_summary = dbc.Table(
                [
                    html.Tbody(
                        [
                            html.Tr([html.Td("Grouping Variable"), html.Td(grouping)]),
                            html.Tr([html.Td("Group 1"), html.Td(group1)]),
                            html.Tr([html.Td("Group 2"), html.Td(group2)]),
                            html.Tr([html.Td("Cell Type Filter"), html.Td(ct)]),
                            html.Tr(
                                [html.Td("Biological Samples"), html.Td(adata.n_obs)]
                            ),
                            html.Tr([html.Td("Samples (Group 1)"), html.Td(group1_n)]),
                            html.Tr([html.Td("Samples (Group 2)"), html.Td(group2_n)]),
                            html.Tr(
                                [
                                    html.Td("Median Cells / Sample"),
                                    html.Td(median_cells),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Median Counts / Sample"),
                                    html.Td(median_counts),
                                ]
                            ),
                            html.Tr(
                                [html.Td("Minimum Cells / Sample"), html.Td(min_cells)]
                            ),
                            html.Tr(
                                [
                                    html.Td("Minimum Counts / Sample"),
                                    html.Td(min_counts),
                                ]
                            ),
                        ]
                    )
                ]
            )

            pseudobulk_items.append(
                dbc.AccordionItem(
                    pseudobulk_summary,
                    title=f"Pseudobulk summary for {ct}",
                    item_id=f"pseudobulk-{completed}",
                )
            )

            # Per-celltype DE result table with native sortable columns.
            if hasattr(results, "reset_index"):
                results_table_df = results.reset_index()
                de_table_content = dash_table.DataTable(
                    id={"type": "de-results-table", "celltype": str(ct)},
                    columns=[
                        {"name": col, "id": col} for col in results_table_df.columns
                    ],
                    data=results_table_df.to_dict("records"),
                    sort_action="native",
                    sort_mode="single",
                    page_size=20,
                    style_table={"overflowX": "auto"},
                )
            else:
                de_table_content = html.Div(
                    f"DE results for {ct} are not available in table format."
                )

            de_items.append(
                dbc.AccordionItem(
                    de_table_content,
                    title=f"DE results for {ct}",
                    item_id=f"de-{completed}",
                )
            )

            # Convert the DE results into volcano-plot inputs and label each point
            # by significance / direction so the plot can be color-coded clearly.
            # Build a volcano plot for this cell type using DE outputs.
            volcano_content = html.Div(f"Volcano plot for {ct} is not available.")
            if hasattr(results, "reset_index"):
                volcano_df = _normalize_de_result_gene_column(
                    results.reset_index().copy(),
                    ct,
                )

                volcano_df["log2FoldChange"] = pd.to_numeric(
                    volcano_df.get("log2FoldChange"), errors="coerce"
                )
                volcano_df["padj"] = pd.to_numeric(
                    volcano_df.get("padj"), errors="coerce"
                )

                volcano_df = volcano_df[
                    volcano_df["log2FoldChange"].notna()
                    & volcano_df["padj"].notna()
                    & (volcano_df["padj"] > 0)
                ].copy()

                if not volcano_df.empty:
                    volcano_df["neg_log10_padj"] = -np.log10(volcano_df["padj"])
                    volcano_df["regulation"] = "not significant"
                    volcano_df.loc[
                        (volcano_df["padj"] < 0.05)
                        & (volcano_df["log2FoldChange"] > 0),
                        "regulation",
                    ] = "upregulated"
                    volcano_df.loc[
                        (volcano_df["padj"] < 0.05)
                        & (volcano_df["log2FoldChange"] < 0),
                        "regulation",
                    ] = "downregulated"

                    hover_fields = {
                        "padj": ":.3e",
                        "log2FoldChange": ":.3f",
                        "regulation": True,
                    }
                    if "gene" in volcano_df.columns:
                        hover_fields["gene"] = True

                    fig = px.scatter(
                        volcano_df,
                        x="log2FoldChange",
                        y="neg_log10_padj",
                        color="regulation",
                        color_discrete_map={
                            "not significant": "grey",
                            "downregulated": "blue",
                            "upregulated": "red",
                        },
                        title=f"Volcano plot for {ct}",
                        hover_data=hover_fields,
                    )
                    fig.update_layout(legend_title_text="")
                    volcano_content = dcc.Graph(figure=fig)

            volcano_items.append(
                dbc.AccordionItem(
                    volcano_content,
                    title=f"Volcano plot for {ct}",
                    item_id=f"volcano-{completed}",
                )
            )

            # Build a top-20 DE gene heatmap for this cell type.
            heatmap_content = html.Div(f"Heatmap for {ct} is not available.")
            if hasattr(results, "reset_index"):
                heatmap_df = _normalize_de_result_gene_column(
                    results.reset_index().copy(),
                    ct,
                )

                if "gene" in heatmap_df.columns and "padj" in heatmap_df.columns:
                    heatmap_df["padj"] = pd.to_numeric(
                        heatmap_df["padj"], errors="coerce"
                    )
                    if "log2FoldChange" in heatmap_df.columns:
                        heatmap_df["log2FoldChange"] = pd.to_numeric(
                            heatmap_df["log2FoldChange"], errors="coerce"
                        )
                        heatmap_df["abs_log2fc"] = heatmap_df["log2FoldChange"].abs()
                    else:
                        heatmap_df["abs_log2fc"] = 0.0

                    top_genes_df = heatmap_df[
                        heatmap_df["gene"].notna() & heatmap_df["padj"].notna()
                    ].copy()
                    top_genes_df = top_genes_df.sort_values(
                        ["padj", "abs_log2fc"], ascending=[True, False]
                    )
                    top_genes = top_genes_df["gene"].astype(str).tolist()[:20]
                    print(
                        f"[DE heatmap debug] celltype={ct} total_de_rows={len(heatmap_df)} "
                        f"candidate_top_genes={len(top_genes)}"
                    )

                    available_top_genes = [g for g in top_genes if g in adata.var_names]
                    print(
                        f"[DE heatmap debug] celltype={ct} genes_in_adata={len(available_top_genes)} "
                        f"grouping_present={grouping in adata.obs.columns}"
                    )
                    if available_top_genes and grouping in adata.obs.columns:
                        heatmap_subset = adata[:, available_top_genes].copy()
                        print(
                            f"[DE heatmap debug] celltype={ct} heatmap_subset_shape="
                            f"{heatmap_subset.n_obs}x{heatmap_subset.n_vars}"
                        )

                        if issparse(heatmap_subset.X):
                            heatmap_values = heatmap_subset.X.toarray()
                        else:
                            heatmap_values = np.asarray(heatmap_subset.X)

                        # Log-transform pseudobulk counts for more interpretable colour scaling.
                        heatmap_values = np.log1p(heatmap_values.astype(float))

                        # Sort samples by selected grouping to make group separation visible.
                        sample_order = np.argsort(
                            heatmap_subset.obs[grouping].astype(str).to_numpy(),
                            kind="stable",
                        )
                        heatmap_values = heatmap_values[sample_order, :]
                        ordered_obs = heatmap_subset.obs.iloc[sample_order]

                        # Z-score per gene across samples to emphasize relative differences.
                        gene_means = heatmap_values.mean(axis=0, keepdims=True)
                        gene_stds = heatmap_values.std(axis=0, keepdims=True)
                        gene_stds[gene_stds == 0] = 1.0
                        heatmap_z = (heatmap_values - gene_means) / gene_stds

                        sample_labels = [
                            f"{sample} ({grp})"
                            for sample, grp in zip(
                                ordered_obs.index.astype(str),
                                ordered_obs[grouping].astype(str),
                            )
                        ]

                        heatmap_fig = px.imshow(
                            heatmap_z.T,
                            x=sample_labels,
                            y=available_top_genes,
                            color_continuous_scale="RdBu_r",
                            aspect="auto",
                            labels={
                                "x": "Pseudobulk Samples",
                                "y": "Top DE Genes",
                                "color": "Z-score",
                            },
                            title=f"Top 20 DE genes heatmap for {ct}",
                        )
                        heatmap_fig.update_layout(xaxis_tickangle=45)
                        heatmap_content = dcc.Graph(figure=heatmap_fig)
                        print(f"[DE heatmap debug] celltype={ct} heatmap_rendered=True")
                    else:
                        if not available_top_genes:
                            print(
                                f"[DE heatmap debug] celltype={ct} heatmap skipped: "
                                "no top genes overlap adata.var_names"
                            )
                        if grouping not in adata.obs.columns:
                            print(
                                f"[DE heatmap debug] celltype={ct} heatmap skipped: "
                                f"grouping column '{grouping}' missing in pseudobulk obs"
                            )
                else:
                    print(
                        f"[DE heatmap debug] celltype={ct} heatmap skipped: "
                        f"required columns missing, found={list(heatmap_df.columns)}"
                    )
            else:
                print(
                    f"[DE heatmap debug] celltype={ct} heatmap skipped: "
                    f"results object has no reset_index (type={type(results)})"
                )

            heatmap_items.append(
                dbc.AccordionItem(
                    heatmap_content,
                    title=f"Heatmap for {ct}",
                    item_id=f"heatmap-{completed}",
                )
            )

        if completed == 0:
            return "No valid cell type analyses could be completed.", "", "", "", ""

        logger.info(
            "Running differential expression analysis for grouping '%s', comparing '%s' vs '%s', filtered by cell type '%s'.",
            grouping,
            group1,
            group2,
            celltype,
        )

        de_results = f"Differential expression analysis completed successfully for {completed} cell type(s)."
        # Wrap each result type in its own accordion so every cell type remains
        # collapsed by default and the output stays compact.
        pseudobulk_output = dbc.Accordion(
            pseudobulk_items,
            start_collapsed=True,
            always_open=True,
            flush=True,
            id="pseudobulk-accordion",
        )
        de_output = dbc.Accordion(
            de_items,
            start_collapsed=True,
            always_open=True,
            flush=True,
            id="de-results-accordion",
        )
        volcano_output = dbc.Accordion(
            volcano_items,
            start_collapsed=True,
            always_open=True,
            flush=True,
            id="volcano-results-accordion",
        )
        heatmap_output = dbc.Accordion(
            heatmap_items,
            start_collapsed=True,
            always_open=True,
            flush=True,
            id="de-heatmap-accordion",
        )

        return de_results, pseudobulk_output, de_output, volcano_output, heatmap_output
