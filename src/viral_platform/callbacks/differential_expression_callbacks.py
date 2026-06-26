import logging
import numpy as np
import pandas as pd
import plotly.express as px

from dash import Input, Output, State, html, no_update, dash_table, dcc
import dash_bootstrap_components as dbc

from viral_platform.state.dataset_store import get_state_store, get_working_dataset, reset_state_store
from viral_platform.analysis.pseudobulk import subset_cells, find_biological_replicates, create_pseudobulk
from viral_platform.analysis.differential_expression import run_differential_expression

logger = logging.getLogger(__name__)


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


def register_differential_expression_callbacks(app):
    """Register callbacks that keep DE dropdown options synchronized with dataset metadata/state."""
    @app.callback(
        Output("grouping-variable-dropdown", "options"),
        Output("grouping-variable-dropdown", "value"),
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

        cell_types = metadata_info.get("cell_types", [])
        celltype_options = _build_options(cell_types)
        celltype_value = celltype_options[0]["value"] if celltype_options else None

        if not grouping_options:
            grouping_options = [{"label": "Upload a dataset to select grouping variable", "value": ""}]
            grouping_value = ""

        if not celltype_options:
            celltype_options = [{"label": "Upload a dataset to select cell type", "value": ""}]
            celltype_value = ""

        logger.info(
            "Populated DE metadata dropdowns with %s grouping columns and %s cell types.",
            len(grouping_options),
            len(celltype_options),
        )
        return grouping_options, grouping_value, celltype_options, celltype_value

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
                [{"label": "Select a grouping variable to select group 1", "value": ""}],
                "",
                [{"label": "Select a grouping variable to select group 2", "value": ""}],
                "",
            )

        if not grouping_column or grouping_column not in adata.obs.columns:
            return (
                [{"label": "Select a grouping variable to select group 1", "value": ""}],
                "",
                [{"label": "Select a grouping variable to select group 2", "value": ""}],
                "",
            )

        unique_values = adata.obs[grouping_column].dropna().astype(str).unique().tolist()
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
        Input("run-differential-expression-analysis-button", "n_clicks"),
        State("grouping-variable-dropdown", "value"),
        State("group1-dropdown", "value"),
        State("group2-dropdown", "value"),
        State("celltype-dropdown", "value"),
    )
    def run_DE_analysis(n_clicks, grouping, group1, group2, celltype):
        """Run differential expression analysis when the button is clicked."""
        if n_clicks == 0:
            return "", "Upload a dataset to run differential expression analysis.", "", ""

        # Build the analysis target list: a single selected cell type, or every
        # discovered cell type when the user requests the "All Cells" mode.
        if celltype != "All Cells":
            target_celltypes = [celltype]
        else:
            state = get_state_store()
            metadata_info = state.get("metadata_info", {})
            target_celltypes = [
                ct for ct in metadata_info.get("cell_types", [])
                if str(ct).strip().lower() != "all cells"
            ]

        if not target_celltypes:
            return "No cell types available for differential expression analysis.", "", "", ""

        # Keep unique order in case metadata_info has duplicates.
        target_celltypes = list(dict.fromkeys(target_celltypes))

        pseudobulk_items = []
        de_items = []
        volcano_items = []
        completed = 0

        # Run the full DE pipeline independently for each target cell type so
        # each section can be rendered as its own collapsible output.
        for ct in target_celltypes:
            adata = subset_cells(grouping, group1, group2, ct)
            if adata is None:
                logger.warning("Skipping DE for cell type '%s' due to missing/invalid subset.", ct)
                continue

            adata, results = run_differential_expression(adata, grouping, group1, group2, ct)
            if adata is None or not hasattr(adata, "obs"):
                logger.warning("Skipping DE for cell type '%s' due to failed DE analysis.", ct)
                continue

            completed += 1

            if grouping in adata.obs.columns:
                group1_n = adata.obs[adata.obs[grouping] == group1]["sampleID"].nunique() if "sampleID" in adata.obs.columns else "N/A"
                group2_n = adata.obs[adata.obs[grouping] == group2]["sampleID"].nunique() if "sampleID" in adata.obs.columns else "N/A"
            else:
                group1_n = "N/A"
                group2_n = "N/A"

            median_cells = int(adata.obs["psbulk_cells"].median()) if "psbulk_cells" in adata.obs.columns else "N/A"
            median_counts = int(adata.obs["psbulk_counts"].median()) if "psbulk_counts" in adata.obs.columns else "N/A"
            min_cells = int(adata.obs["psbulk_cells"].min()) if "psbulk_cells" in adata.obs.columns else "N/A"
            min_counts = int(adata.obs["psbulk_counts"].min()) if "psbulk_counts" in adata.obs.columns else "N/A"

            # Per-celltype pseudobulk summary table.
            pseudobulk_summary = dbc.Table(
                [
                    html.Tbody([
                        html.Tr([html.Td("Grouping Variable"), html.Td(grouping)]),
                        html.Tr([html.Td("Group 1"), html.Td(group1)]),
                        html.Tr([html.Td("Group 2"), html.Td(group2)]),
                        html.Tr([html.Td("Cell Type Filter"), html.Td(ct)]),
                        html.Tr([html.Td("Biological Samples"), html.Td(adata.n_obs)]),
                        html.Tr([html.Td("Samples (Group 1)"), html.Td(group1_n)]),
                        html.Tr([html.Td("Samples (Group 2)"), html.Td(group2_n)]),
                        html.Tr([html.Td("Median Cells / Sample"), html.Td(median_cells)]),
                        html.Tr([html.Td("Median Counts / Sample"), html.Td(median_counts)]),
                        html.Tr([html.Td("Minimum Cells / Sample"), html.Td(min_cells)]),
                        html.Tr([html.Td("Minimum Counts / Sample"), html.Td(min_counts)]),
                    ])
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
                    columns=[{"name": col, "id": col} for col in results_table_df.columns],
                    data=results_table_df.to_dict("records"),
                    sort_action="native",
                    sort_mode="single",
                    page_size=20,
                    style_table={"overflowX": "auto"},
                )
            else:
                de_table_content = html.Div(f"DE results for {ct} are not available in table format.")

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
                volcano_df = results.reset_index().copy()
                if "index" in volcano_df.columns:
                    volcano_df = volcano_df.rename(columns={"index": "gene"})

                volcano_df["log2FoldChange"] = pd.to_numeric(volcano_df.get("log2FoldChange"), errors="coerce")
                volcano_df["padj"] = pd.to_numeric(volcano_df.get("padj"), errors="coerce")

                volcano_df = volcano_df[
                    volcano_df["log2FoldChange"].notna()
                    & volcano_df["padj"].notna()
                    & (volcano_df["padj"] > 0)
                ].copy()

                if not volcano_df.empty:
                    volcano_df["neg_log10_padj"] = -np.log10(volcano_df["padj"])
                    volcano_df["regulation"] = "not significant"
                    volcano_df.loc[
                        (volcano_df["padj"] < 0.05) & (volcano_df["log2FoldChange"] > 0),
                        "regulation",
                    ] = "upregulated"
                    volcano_df.loc[
                        (volcano_df["padj"] < 0.05) & (volcano_df["log2FoldChange"] < 0),
                        "regulation",
                    ] = "downregulated"

                    hover_fields = {"padj": ":.3e", "log2FoldChange": ":.3f", "regulation": True}
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

        if completed == 0:
            return "No valid cell type analyses could be completed.", "", "", ""

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

        return de_results, pseudobulk_output, de_output, volcano_output