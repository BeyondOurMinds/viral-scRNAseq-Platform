from dash import Input, Output, State, html, no_update
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_working_dataset, get_state_store, set_working_dataset, sync_state_with_dataset
import numpy as np
import logging

logger = logging.getLogger(__name__)

def viral_burden_results(adata):
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

def register_viral_burden_callbacks(app):
    @app.callback(
        Output("viral-burden-loading-signal", "children"),
        Output("viral-burden-results-container", "children"),
        Output("viral-burden-associations-container", "hidden"),
        Input("run-viral-burden-analysis-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def run_viral_burden_analysis(n_clicks):
        """
        Calculates viral burden for each cell.

        Parameters
        ----------
        adata : AnnData
            Dataset containing expression matrix.

        detected_features : list
            List of viral feature names returned by the viral
            detection module.

        Returns
        -------
        AnnData
            The input AnnData with new columns added to adata.obs.
        """
        if n_clicks is None or n_clicks == 0:
            return no_update, "No viral burden results yet. Run the analysis to see results here."
        
        history = get_state_store()
        adata = get_working_dataset()
        if adata is None:
            return "done", "No dataset available for viral burden analysis."
        
        features = history.get("viral_detection", {}).get("viral_features", "")
        history = None # remove local history object to free memory
        if not features:
            return "done", "No viral features detected. Please run viral gene detection first."

        if isinstance(features, str):
            features = [f.strip() for f in features.split(",") if f.strip()]
        else:
            features = [f for f in features if f]

        if not features:
            return "done", "No valid viral features detected. Please run viral gene detection first."
        
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

        return "done", viral_burden_results(adata), False