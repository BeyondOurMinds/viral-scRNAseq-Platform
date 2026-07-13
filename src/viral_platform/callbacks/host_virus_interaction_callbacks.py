from dash import Input, Output, State, dash_table, html, no_update, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_working_dataset, get_state_store, set_working_dataset, sync_state_with_dataset
from viral_platform.analysis.host_virus_interaction import host_virus_interaction, get_features_for_gene
import logging
import numpy as np


logger = logging.getLogger(__name__)

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

def register_host_virus_interaction_callbacks(app):
    @app.callback(
        Output("host-virus-interaction-loading-signal", "children"),
        Output("host-virus-interaction-results-container", "children"),
        Output("host-virus-interaction-summary-container", "children"),
        Input("run-host-virus-interaction-analysis-button", "n_clicks"),
        State("host-virus-interaction-dropdown", "value"),
        prevent_initial_call=True,
    )
    def run_host_virus_interaction_analysis(n_clicks, selected_gene):
        """
        Calculates host-virus interactions based on viral burden and host gene expression.

        Parameters
        ----------
        n_clicks : int
            Number of times the "Run Host-Virus Interaction Analysis" button has been clicked.
        selected_gene : str
            The selected viral gene for which to analyze host-virus interactions.

        Returns
        -------
        tuple
            A tuple containing:
            - A string indicating the loading status.
            - A Dash DataTable displaying the host-virus interaction results.
        """
        if not n_clicks or n_clicks == 0:
            return no_update, "No host-virus interaction results yet. Run the analysis to see results here.", ""
        history = get_state_store()
        adata = get_working_dataset()
        if adata is None:
            return "done", "No dataset available for viral burden analysis.", ""
        
        features = history.get("viral_detection", {}).get("viral_features", "")
        history = None # remove local history object to free memory
        if not features:
            return "done", "No viral features detected. Please run viral gene detection first.", ""

        if isinstance(features, str):
            features = [f.strip() for f in features.split(",") if f.strip()]
        else:
            features = [f for f in features if f]

        if not features:
            return "done", "No valid viral features detected. Please run viral gene detection first.", ""
        
        viral_gene_features = get_features_for_gene(adata, selected_gene)
        
        # Run host-virus interaction analysis
        results = host_virus_interaction(adata, features, selected_gene, viral_gene_features)

        # results table
        if results.empty:
            return "", "No significant host-virus interactions found.", ""
        
        # summary table
        hsi_summary = dbc.Table(
            [
                html.Tbody([
                    html.Th("Host-Virus Interaction Summary", colSpan=2, style={"textAlign": "center", "fontWeight": "bold"}),
                    html.Tr([html.Td("Selected Viral Gene:"), html.Td(f"{selected_gene}")]),
                    html.Tr([html.Td("Viral Features Used:"), html.Td(len(viral_gene_features))]),
                    html.Tr([html.Td("Total Host Genes Tested:"), html.Td(f"{results.shape[0]}")]),
                    html.Tr([html.Td("Significant Host Genes (p.adj < 0.05):"), html.Td(f"{(results['adjusted_p'] < 0.05).sum()}")]),
                    html.Tr([html.Td("Significant Positive Correlations (corr > 0.15):"), html.Td(f"{((results['correlation'] >= 0.15) & (results['adjusted_p'] < 0.05)).sum()}")]),
                    html.Tr([html.Td("Significant Negative Correlations (corr < -0.15):"), html.Td(f"{((results['correlation'] <= -0.15) & (results['adjusted_p'] < 0.05)).sum()}")]),
                ])
            ]
        )
        
        
        return "", make_sortable_table(results, "host-virus-interaction-results-table"), hsi_summary