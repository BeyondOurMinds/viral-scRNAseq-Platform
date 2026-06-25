import logging

from dash import Input, Output, State

from viral_platform.state.dataset_store import get_state_store, get_working_dataset
from viral_platform.analysis.pseudobulk import subset_cells, find_biological_replicates, create_pseudobulk

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
        Input("run-differential-expression-analysis-button", "n_clicks"),
        State("grouping-variable-dropdown", "value"),
        State("group1-dropdown", "value"),
        State("group2-dropdown", "value"),
        State("celltype-dropdown", "value"),
    )
    def run_DE_analysis(n_clicks, grouping, group1, group2, celltype):
        """Run differential expression analysis when the button is clicked."""
        if n_clicks == 0:
            return ""
        
        adata = subset_cells(grouping, group1, group2, celltype)
        if adata is None:
            logger.warning("Differential expression analysis requested without an active dataset.")
            return "No active dataset available for differential expression analysis."
        if not find_biological_replicates(adata, grouping):
            return "Insufficient biological replicates for differential expression analysis."
        adata = create_pseudobulk(adata, grouping)
        if adata is None:
            return "Failed to create pseudobulk dataset for differential expression analysis."
        # Here you would implement the actual DE analysis logic
        logger.info(
            "Running differential expression analysis for grouping '%s', comparing '%s' vs '%s', filtered by cell type '%s'.",
            grouping,
            group1,
            group2,
            celltype,
        )
        
        # Placeholder for DE analysis result
        de_results = "Differential expression analysis completed successfully."
        
        return de_results