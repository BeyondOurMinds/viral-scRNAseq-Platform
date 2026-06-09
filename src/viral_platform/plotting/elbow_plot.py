import plotly.express as px
from viral_platform.state.dataset_store import get_working_dataset
import pandas as pd
from dash import dcc, html

def create_elbow_plot(adata=None):
    if adata is None:
        adata = get_working_dataset()
    if adata is None:
        raise ValueError("No dataset available for elbow plot.")
    
    try:
        pca_data = adata.obsm.get("X_pca", None)
        if pca_data is None:
            raise ValueError("PCA data not found in the dataset. Please run PCA before creating the elbow plot.")
        
        explained_variance_ratio = adata.uns.get("pca", {}).get("variance_ratio", None)
        if explained_variance_ratio is None:
            raise ValueError("Explained variance ratio not found in the dataset. Please run PCA before creating the elbow plot.")
        
        df = pd.DataFrame({
            "Principal Component": [f"PC{i+1}" for i in range(len(explained_variance_ratio))],
            "Explained Variance Ratio": explained_variance_ratio
        })
        
        fig = px.bar(df, x="Principal Component", y="Explained Variance Ratio", title="Elbow Plot")
        fig.update_layout(xaxis_title="Principal Components", yaxis_title="Explained Variance Ratio")
        return html.Div([
            dcc.Graph(figure=fig, id="elbow-plot"),
            dcc.Slider(
                id="pc-slider",
                min=1,
                max=len(explained_variance_ratio),
                step=1,
                value=10,
                marks={i: f"PC{i}" for i in range(1, len(explained_variance_ratio)+1)},
            ),
            html.Button("Apply PCA Selection", id="select-pcs-button", n_clicks=0, style={"marginTop": "20px"}),
            html.Div(id="selected-pcs-output", style={"marginTop": "10px", "fontWeight": "bold"}, children="Select PCs to begin clustering analysis.")
        ])
    except Exception as exc:
        raise RuntimeError("Failed to create elbow plot: " + str(exc)) from exc