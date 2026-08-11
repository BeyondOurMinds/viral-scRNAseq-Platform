from dash import Input, Output, State, dash_table, html, no_update
import pandas as pd
import dash_bootstrap_components as dbc
from viral_platform.analysis.viral_gene_detection import list_viral_gene_sets
from viral_platform.state.dataset_store import cache_results, get_working_dataset, get_state_store, update_state_store
from viral_platform.analysis.host_virus_interaction import host_virus_interaction, get_features_for_gene
from viral_platform.analysis.Intact import load_intact_reference, find_intact_interactions, summarize_intact_interactions, get_significant_de_genes, get_de_genes_for_celltype, run_intact_interpretation
import logging


logger = logging.getLogger(__name__)

INTACT_VIRUS_TAXIDS = {
    "EBV": {
        "10376",
        "10377",
        "82830",
    },

    "HIV": {
        "11676",
    },

    "SARS-CoV-2": {
        "2697049",
    },

    "Influenza A": {
        "381512",
        "382835",
        "284218",
        "480024",
    },

    "Influenza B": {
        "11122",
    },

    "RSV": {
        "269446",
        "11259",
        "11250",
    },

    "Zika": {
        "64320",
    },
}


def _build_dropdown_options(values):
    """Build deterministic dropdown options from string values."""
    return [{"label": value, "value": value} for value in sorted({str(v) for v in values if str(v).strip()})]

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
        Output("host-virus-interaction-dropdown", "options"),
        Output("host-virus-interaction-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_host_virus_dropdown(_dataset_version):
        """Populate selectable viral genes from shared viral-detection state."""
        history = get_state_store()
        raw_genes = history.get("viral_detection", {}).get("viral_genes", "")

        if isinstance(raw_genes, str):
            genes = [gene.strip() for gene in raw_genes.split(",") if gene.strip()]
        else:
            genes = [str(gene).strip() for gene in raw_genes if str(gene).strip()]

        options = _build_dropdown_options(genes)
        if not options:
            return [{"label": "Run viral gene detection first", "value": ""}], ""

        return options, options[0]["value"]

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
            return no_update, no_update, no_update
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

        sig_host_genes = results[results["adjusted_p"] < 0.05]
        update_state_store(**{"host-virus-interaction": {"sig_host_genes": sig_host_genes["gene"].tolist()}})
        
        
        table = make_sortable_table(results, "host-virus-interaction-results-table")
        cache_results(**{
            "host-virus-interaction-results-container": table,
            "host-virus-interaction-summary-container": hsi_summary,
        })
        return "", table, hsi_summary
    
    @app.callback(
		Output("host-virus-interaction-interpretation-dropdown", "options"),
		Input("host-virus-interaction-interpretation-dropdown", "id"),
	)
    def populate_viral_set_options(_):
        """Populate host-virus interaction interpretation dropdown options from files available on disk.

        Inputs: ignored trigger value.
        Outputs: list[dict] dropdown options.
        Interacts with: list_host_virus_interpretation_sets.
        """
        options = []
        options.extend({"label": set_name, "value": set_name} for set_name in list_viral_gene_sets())
        return options
    
    @app.callback(
        Output("hvi-interpretation-celltype-dropdown-container", "hidden"),
        Output("custom-hvi-gene-list-container", "hidden"),
        Input("host-virus-interaction-gene-source-dropdown", "value"),
    )
    def toggle_celltype_dropdown(gene_source):
        """Toggle visibility of the cell type dropdown based on the selected gene source.

        Inputs: gene_source (str) - selected gene source from the dropdown.
        Outputs: hidden (bool) - whether to hide the cell type dropdown.
        """
        if gene_source == "deg":
            return False, True  # Show the cell type dropdown for DEGs
        elif gene_source == "custom":
            return True, False  # Show the custom gene list input for custom gene source
        return True, True  # Hide both for other gene sources
    
    @app.callback(
        Output("hvi-interpretation-celltype-dropdown", "options"),
        Output("hvi-interpretation-celltype-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_hvi_interpretation_celltype_dropdown(dataset_version):
        """
        Populate the cell type dropdown for host-virus interaction interpretation based on available DE results.
        """
        # Access the global state to get the DE results by cell type
        state = get_state_store()
        de_results_by_celltype = state.get("DE_results", {}).get("results_by_celltype", {})
        
        # Extract cell types from the keys of the DE results dictionary
        cell_types = list(de_results_by_celltype.keys())
        
        # Create options for the dropdown
        options = [{"label": "All Cells", "value": "_all_"}]
        options.extend({"label": ct, "value": ct} for ct in cell_types)
        
        # Set a default value if there are available cell types
        default_value = cell_types[0] if cell_types else None
        
        return options, default_value
    
    @app.callback(
        Output("host-virus-interaction-interpretation-loading-signal", "children"),
        Output("host-virus-interaction-interpretation-results-container", "children"),
        Input("run-host-virus-interaction-interpretation-button", "n_clicks"),
        State("host-virus-interaction-interpretation-dropdown", "value"),
        State("host-virus-interaction-gene-source-dropdown", "value"),
        State("hvi-interpretation-celltype-dropdown", "value"),
        State("custom-hvi-gene-list-input", "value"),
        prevent_initial_call=True,
    )
    def run_host_virus_interaction_interpretation(n_clicks, selected_virus, gene_source, selected_celltype, custom_gene_list):
        """
        """

        if not n_clicks or n_clicks == 0:
            return no_update, no_update
        
        intact_df = load_intact_reference(
            r"src\viral_platform\intact\intact_virus_host.tsv"
        )

        virus_taxids = INTACT_VIRUS_TAXIDS.get(
            selected_virus,
            set(),
        )

        if not virus_taxids:
            return "done", f"No IntAct reference data found for virus: {selected_virus}."

        intact_virus = intact_df[
            intact_df["virus_taxid"].isin(virus_taxids)
        ].copy()
        
        if gene_source == "deg":
            # Load DE results for the selected cell type
            state = get_state_store()
            de_results_by_celltype = state.get("DE_results", {}).get("results_by_celltype", {})

            for celltype, df in de_results_by_celltype.items():
                print(f"\nCell type: {celltype}")
                print("Columns:", list(df.columns))
                print(df.head())

            if selected_celltype == "_all_":
                # Combine DE results from all cell types
                gene_to_celltypes = get_significant_de_genes(
                    de_results_by_celltype
                )
                genes = list(gene_to_celltypes.keys())
            else:
                de_results = de_results_by_celltype[selected_celltype]
                if de_results is None:
                    return "done", f"No DE results found for cell type: {selected_celltype}."
                genes = get_de_genes_for_celltype(de_results_by_celltype, selected_celltype)
                gene_to_celltypes = {
                    gene: [selected_celltype]
                    for gene in genes
                }
            
            raw_matches, summary = run_intact_interpretation(
                intact_virus,
                genes,
                gene_to_celltypes,
            )

            # results table
            if raw_matches.empty:
                return "done", f"No significant host-virus interactions found for virus: {selected_virus} and cell type: {selected_celltype}."
            
        elif gene_source == "isg":
            # Load ISG genes from the state
            gene_list =[]
            state = get_state_store()
            genes = state.get("isg_detection", {}).get("isg_genes", [])
            gene_list = [gene.strip() for gene in genes.split(",") if gene.strip()]
            print(f"ISG genes: {gene_list}")
            raw_matches, summary = run_intact_interpretation(
                intact_virus,
                gene_list,
            )
        elif gene_source == "hvi":
            # Load significant host genes from the state
            state = get_state_store()
            genes = state.get("host-virus-interaction", {}).get("sig_host_genes", [])
            print(f"Significant host genes: {genes}")
            raw_matches, summary = run_intact_interpretation(
                intact_virus,
                genes,
            )
        elif gene_source == "custom":
            if not custom_gene_list:
                return "done", "No custom gene list provided."
            genes = [gene.strip() for gene in custom_gene_list.split(",") if gene.strip()]
            raw_matches, summary = run_intact_interpretation(
                intact_virus,
                genes,
            )

        table = make_sortable_table(summary, "host-virus-interaction-interpretation-results-table")
        cache_results(**{
        "host-virus-interaction-interpretation-results-container": table})

        return "done", table
        
