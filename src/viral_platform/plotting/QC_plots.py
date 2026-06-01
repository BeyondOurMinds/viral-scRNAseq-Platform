import plotly.express as px
from dash import dcc, html
import scanpy as sc
from viral_platform.state.dataset_store import set_working_dataset

def create_qc_plots(adata):
    if adata is None:
        return "No dataset available for QC plotting."

    # Mark mitochondrial genes so scanpy computes pct_counts_mt.
    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")

    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars=["mt"],
        inplace=True,
    )
    set_working_dataset(adata)

    required_cols = ["total_counts", "n_genes_by_counts", "pct_counts_mt"]
    missing_cols = [col for col in required_cols if col not in adata.obs]
    if missing_cols:
        return f"Missing QC metrics after calculation: {', '.join(missing_cols)}"

    adata.obs["nCount_RNA"] = adata.obs["total_counts"]
    adata.obs["nFeature_RNA"] = adata.obs["n_genes_by_counts"]
    adata.obs["percent.mt"] = adata.obs["pct_counts_mt"]

    ncount_fig = px.violin(
        adata.obs,
        y="nCount_RNA",
        box=True,
        points=False,
        title="nCount_RNA",
    )
    ncount_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Counts")

    nfeature_fig = px.violin(
        adata.obs,
        y="nFeature_RNA",
        box=True,
        points=False,
        title="nFeature_RNA",
    )
    nfeature_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Features")

    percent_mt_fig = px.violin(
        adata.obs,
        y="percent.mt",
        box=True,
        points=False,
        title="percent.mt",
    )
    percent_mt_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Percent")

    return html.Div([
        dcc.Graph(figure=ncount_fig, id="ncount-violin"),
        dcc.Slider(
            id="min-counts-slider",
            min=0,
            max=adata.obs["nCount_RNA"].max(),
            step=100,
        ),
        dcc.Graph(figure=nfeature_fig, id="nfeature-violin"),
        dcc.Slider(
            id="min-features-slider",
            min=0,
            max=adata.obs["nFeature_RNA"].max(),
            step=10,
        ),
        dcc.Graph(figure=percent_mt_fig, id="percent-mt-violin"),
        dcc.Slider(
            id="max-percent-mt-slider",
            min=0,
            max=adata.obs["percent.mt"].max(),
            step=1,
        ),
    ])

