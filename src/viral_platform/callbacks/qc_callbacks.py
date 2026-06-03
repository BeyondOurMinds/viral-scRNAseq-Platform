from dash import Input, Output, State, no_update
import plotly.express as px

from viral_platform.plotting.QC_plots import create_qc_plots
from viral_platform.state.dataset_store import get_working_dataset, set_working_dataset


def register_qc_callbacks(app):
    @app.callback(
        Output("qc-generate-loading-signal", "children"),
        Output("qc-temp-container", "children"),
        Input("generate-qc-plots-button", "n_clicks")
    )
    def render_qc_plots(n_clicks):
        if n_clicks == 0:
            return no_update, "Upload a dataset to view QC plots."
        adata = get_working_dataset()
        if adata is None:
            return "done", "Upload a dataset to view QC plots."

        return "done", create_qc_plots(adata)
    
    @app.callback(
        Output("ncount-violin", "figure"),
        Input("min-counts-slider", "value")
    )
    def update_ncount_violin(min_counts):
        adata = get_working_dataset()
        
        ncount_fig = px.violin(
            adata.obs,
            y="nCount_RNA",
            box=True,
            points=False,
            title="nCount_RNA",
        )
        ncount_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Counts")

        ncount_fig.add_hline(y=min_counts[0], line_dash="dash", line_color="red", annotation_text="Min Counts", annotation_position="top left")
        ncount_fig.add_hline(y=min_counts[1], line_dash="dash", line_color="red", annotation_text="Max Counts", annotation_position="top right")
        return ncount_fig
    
    @app.callback(
        Output("nfeature-violin", "figure"),
        Input("min-features-slider", "value")
    )
    def update_nfeature_violin(min_features):
        adata = get_working_dataset()
        
        nfeature_fig = px.violin(
            adata.obs,
            y="nFeature_RNA",
            box=True,
            points=False,
            title="nFeature_RNA",
        )
        nfeature_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Features")

        nfeature_fig.add_hline(y=min_features[0], line_dash="dash", line_color="red", annotation_text="Min Features", annotation_position="top left")
        nfeature_fig.add_hline(y=min_features[1], line_dash="dash", line_color="red", annotation_text="Max Features", annotation_position="top right")
        return nfeature_fig
    
    @app.callback(
        Output("percent-mt-violin", "figure"),
        Input("max-percent-mt-slider", "value")
    )
    def update_percent_mt_violin(max_percent_mt):
        adata = get_working_dataset()

        if adata is None:
            return px.violin(title="Percent Mitochondrial Genes")

        if max_percent_mt is None:
            max_percent_mt = adata.obs["percent.mt"].max()
        
        percent_mt_fig = px.violin(
            adata.obs,
            y="percent.mt",
            box=True,
            points=False,
            title="Percent Mitochondrial Genes",
        )
        percent_mt_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Percent")

        percent_mt_fig.add_hline(y=max_percent_mt, line_dash="dash", line_color="red", annotation_text="Max Percent MT", annotation_position="top right")
        return percent_mt_fig
    
    @app.callback(
        Output("qc-plot-container", "children"),
        Input("apply-qc-filters-button", "n_clicks"),
        State("min-counts-slider", "value"),
        State("min-features-slider", "value"),
        State("max-percent-mt-slider", "value")
    )
    def apply_qc_filters(n_clicks, min_counts, min_features, max_percent_mt):
        if n_clicks == 0:
            return no_update
        
        adata = get_working_dataset()
        if adata is None:
            return "No dataset available to apply QC filters."

        # Here you would implement the actual filtering logic based on the slider values
        # For example:
        adata = adata[adata.obs["nCount_RNA"] >= min_counts[0]]
        adata = adata[adata.obs["nCount_RNA"] <= min_counts[1]]
        adata = adata[adata.obs["nFeature_RNA"] >= min_features[0]]
        adata = adata[adata.obs["nFeature_RNA"] <= min_features[1]]
        adata = adata[adata.obs["percent.mt"] <= max_percent_mt]


        set_working_dataset(adata)  # Update the working dataset with the filtered version
        return create_qc_plots(adata)