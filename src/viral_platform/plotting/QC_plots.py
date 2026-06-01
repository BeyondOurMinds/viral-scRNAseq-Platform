import plotly.express as px
from dash import dcc, html
import scanpy as sc

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
        dcc.Graph(figure=ncount_fig),
        dcc.Graph(figure=nfeature_fig),
        dcc.Graph(figure=percent_mt_fig),
    ])

