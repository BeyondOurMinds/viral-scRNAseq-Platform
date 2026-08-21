import logging

from dash import Output, Input, no_update, dcc
from viral_platform.analysis.CellAnnotation import annotate_cells, celltypist_umap
from viral_platform.state.dataset_store import cache_results, get_working_dataset, set_working_dataset



logger = logging.getLogger(__name__)

def register_cell_annotation_callbacks(app):
    @app.callback(
        Output("cell-annotation-loading-signal", "children"),
        Output("cell-annotation-results-container", "children"),
        Input("run-cell-annotation-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def run_cell_annotation(n_clicks):
        if not n_clicks:
            return no_update, no_update
        try:
            adata = get_working_dataset()
            if adata is None:
                logger.warning("Cell annotation requested without an active dataset.")
                return no_update, "No dataset available. Upload and preprocess data first."
            if "log_normalized" not in adata.layers:
                logger.warning("Cell annotation requested before preprocessing generated log_normalized layer.")
                return no_update, "Run preprocessing before cell annotation."

            adata_ct = adata.copy()  # Create a copy of the AnnData object for cell annotation
            adata_ct.X = adata.layers["log_normalized"].copy()  # Use log-normalized expression for cell annotation
            adata_ct = annotate_cells(adata_ct)
            if adata_ct is None:
                logger.warning("Cell annotation completed but no dataset found in state store.")
                return no_update, "Cell annotation completed, but no dataset found."

            # Persist annotation columns back to the canonical working AnnData.
            annotation_cols = [
                "SCJoseki_predicted_celltype",
                "SCJoseki_confidence",
                "SCJoseki_majority_celltype",
            ]
            for col in annotation_cols:
                if col in adata_ct.obs.columns:
                    adata.obs[col] = adata_ct.obs[col].copy()

            set_working_dataset(adata)
            logger.info("Cell annotation completed successfully.")
            fig = celltypist_umap(adata_ct)
            graph = dcc.Graph(figure=fig)
            cache_results(**{"cell-annotation-results-container": graph})
            return no_update, graph
        except Exception as exc:
            logger.exception("Cell annotation failed: %s", str(exc))
            return no_update, f"Cell annotation failed: {str(exc)}"
