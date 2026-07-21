from dash import Input, Output, State, dash_table, html, no_update, dcc
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_working_dataset, get_state_store, set_working_dataset, sync_state_with_dataset, update_state_store
from viral_platform.analysis.CellCellLIANA import run_liana, filter_liana_results, liana_output_table, summarise_celltype_interactions
import logging
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx


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

def _build_options(values):
    """Normalize iterable values into unique Dash dropdown option dictionaries."""
    seen = set()
    options = [
        {"label": "All", "value": "_all_"},
    ]
    for value in values:
        normalized = str(value)
        if normalized in seen:
            continue
        seen.add(normalized)
        options.append({"label": normalized, "value": normalized})
    return options


def create_network_plot(summary, show_labels=True):
    """
    Create a cell-cell communication network.

    Parameters
    ----------
    summary : pd.DataFrame

    Required columns:
        source
        target
        interaction_count
        mean_magnitude
        mean_specificity
    """

    # --------------------------------------------------
    # Build graph
    # --------------------------------------------------

    G = nx.DiGraph()

    for _, row in summary.iterrows():

        G.add_edge(
            row["source"],
            row["target"],
            interactions=row["interaction_count"],
            magnitude=1 - row["mean_magnitude"],
            specificity=1 - row["mean_specificity"],
        )

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    pos = nx.kamada_kawai_layout(G, weight="interactions")

    # Alternative:
    # pos = nx.spring_layout(G, seed=42, k=2.5, iterations=200)

    # --------------------------------------------------
    # Node statistics
    # --------------------------------------------------

    degree = dict(G.degree())

    weighted_degree = dict(
        G.degree(weight="interactions")
    )

    # --------------------------------------------------
    # Normalise node sizes
    # --------------------------------------------------

    min_node = 12
    max_node = 30

    dmin = min(degree.values())
    dmax = max(degree.values())

    # --------------------------------------------------
    # Normalise edge widths
    # --------------------------------------------------

    min_edge = 1
    max_edge = 8

    wmin = summary["interaction_count"].min()
    wmax = summary["interaction_count"].max()

    # --------------------------------------------------
    # Figure
    # --------------------------------------------------

    fig = go.Figure()

    colours = px.colors.sequential.Turbo

    # -----------------------------------
    # Normalise edge colours
    # -----------------------------------

    strength = 1 - summary["mean_magnitude"]

    smin = strength.min()
    smax = strength.max()

    # --------------------------------------------------
    # Draw edges
    # --------------------------------------------------

    for u, v, data in G.edges(data=True):

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        # -----------------------------------
        # Normalise colour across this dataset
        # -----------------------------------

        if smax == smin:

            scaled = 0.5

        else:

            scaled = (
                data["magnitude"] - smin
            ) / (
                smax - smin
            )

        scaled = max(0, min(1, scaled))

        colour_index = int(
            scaled * (len(colours) - 1)
        )

        hex_colour = colours[colour_index]

        r = int(hex_colour[1:3], 16)
        g = int(hex_colour[3:5], 16)
        b = int(hex_colour[5:7], 16)

        alpha = 0.35 + 0.45 * scaled   # 0.25–0.75

        colour = f"rgba({r},{g},{b},{alpha:.2f})"

        # ------------------------------
        # Edge width
        # ------------------------------

        if wmax == wmin:

            edge_width = (min_edge + max_edge) / 2

        else:

            edge_width = (
                min_edge
                + (data["interactions"] - wmin)
                * (max_edge - min_edge)
                / (wmax - wmin)
            )

        # ------------------------------
        # Edge trace
        # ------------------------------

        fig.add_trace(

            go.Scatter(

                x=[x0, x1],
                y=[y0, y1],

                mode="lines",

                line=dict(
                    width=edge_width,
                    color=colour,
                ),

                hoverinfo="text",

                text=(
                    f"<b>{u}</b> → <b>{v}</b><br>"
                    f"Interactions: {data['interactions']}<br>"
                    f"Mean Magnitude: {data['magnitude']:.3f}<br>"
                    f"Mean Specificity: {data['specificity']:.3f}"
                ),

                showlegend=False,

            )

        )

        # ------------------------------
        # Arrow
        # ------------------------------

        fig.add_annotation(

            x=x1,
            y=y1,

            ax=x0,
            ay=y0,

            xref="x",
            yref="y",

            axref="x",
            ayref="y",

            showarrow=True,

            arrowhead=2,
            arrowsize=0.6,
            arrowwidth=max(1.5, edge_width * 0.6),
            arrowcolor=colour,

            text="",

        )

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    node_x = []
    node_y = []

    node_size = []
    node_sizes = {}

    node_colour = []

    node_text = []

    for node in G.nodes():

        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)

        # ------------------------------
        # Node size
        # ------------------------------

        if dmax == dmin:

            size = (min_node + max_node) / 2

        else:

            size = (
                min_node
                + (degree[node] - dmin)
                * (max_node - min_node)
                / (dmax - dmin)
            )

        node_size.append(size)
        node_sizes[node] = size

        # ------------------------------
        # Colour
        # ------------------------------

        node_colour.append(
            weighted_degree[node]
        )

        node_text.append(

            f"<b>{node}</b><br>"
            f"Connected Cell Types: {degree[node]}<br>"
            f"Total Interactions: {weighted_degree[node]}"

        )

    # --------------------------------------------------
    # Draw nodes
    # --------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=node_x,
            y=node_y,

            mode="markers",

            hoverinfo="text",

            hovertext=node_text,

            marker=dict(

                size=node_size,

                color=node_colour,

                colorscale="Viridis",

                showscale=True,

                colorbar=dict(

                    title="Node<br>Connectivity",

                    x=1.02,

                ),

                line=dict(
                    width=2,
                    color="black",
                ),

            ),

            showlegend=False,

        )

    )

    

    # --------------------------------------------------
    # Node Labels
    # --------------------------------------------------

    if show_labels:
        for node in G.nodes():

            x, y = pos[node]

            fig.add_annotation(

                x=x,
                y=y + 0.01 + (node_sizes[node] / 1500),      # Adjust vertical offset as needed

                text=node,

                showarrow=False,

                font=dict(
                    size=12,
                    color="black"
                ),

                xanchor="center",
                yanchor="bottom",

            )



    # --------------------------------------------------
    # Dummy trace for edge colourbar
    # --------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=[None],
            y=[None],

            mode="markers",

            marker=dict(

                colorscale="Turbo",

                cmin=smin,
                cmax=smax,

                color=[smin],

                size=0,

                showscale=True,

                colorbar=dict(

                    title="Edge<br>Strength",

                    tickvals=[
                        smin,
                        (smin + smax) / 2,
                        smax,
                    ],

                    ticktext=[
                        "Weak",
                        "Moderate",
                        "Strong",
                    ],

                    thickness=18,

                    len=0.75,

                    x=1.12,

                ),

            ),

            hoverinfo="skip",

            showlegend=False,

        )

    )
    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    fig.update_layout(

        title="Cell-Cell Communication Network",

        template="plotly_white",

        hovermode="closest",

        xaxis=dict(
            visible=False
        ),

        yaxis=dict(
            visible=False
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),

    )

    return fig

def register_ccc_callbacks(app):
    @app.callback(
        Output("ccc-source-filter-dropdown", "options"),
        Output("ccc-source-filter-dropdown", "value"),
        Output("ccc-target-filter-dropdown", "options"),
        Output("ccc-target-filter-dropdown", "value"),
        Input("ccc-grouping-dropdown", "value"),
        Input("active-dataset-version", "data"),
    )
    def populate_group_comparison_dropdowns(grouping_column, _dataset_version):
        """Populate source/target dropdowns with unique values from the selected grouping column."""
        adata = get_working_dataset()
        if adata is None:
            return (
                [{"label": "Select source cell type", "value": ""}],
                "",
                [{"label": "Select target cell type", "value": ""}],
                "",
            )

        if not grouping_column or grouping_column not in adata.obs.columns:
            return (
                [{"label": "Select source cell type", "value": ""}],
                "",
                [{"label": "Select target cell type", "value": ""}],
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
        group2_value = options[0]["value"]

        logger.info(
            "Populated DE group dropdowns for '%s' with %s group values.",
            grouping_column,
            len(options),
        )
        return options, group1_value, options, group2_value
    @app.callback(
        Output("ccc-loading-signal", "children"),
        Output("ccc-summary-container", "children", allow_duplicate=True),
        Output("ccc-bubble-plot-container", "children", allow_duplicate=True),
        Output("ccc-network-plot-container", "children", allow_duplicate=True),
        Input("run-ccc-button", "n_clicks"),
        State("ccc-grouping-dropdown", "value"),
        State("ccc-method-dropdown", "value"),
        State("ccc-resource-dropdown", "value"),
        prevent_initial_call=True,
    )
    def run_ccc_analysis(n_clicks, grouping_variable, method, resource):
        """
        Runs the Cell-Cell Communication (CCC) analysis using the selected parameters.

        Parameters
        ----------
        n_clicks : int
            Number of times the "Run Cell-Cell Communication" button has been clicked.
        grouping_variable : str
            The selected grouping variable for the CCC analysis.
        method : str
            The selected method for the CCC analysis.
        resource : str
            The selected resource for the CCC analysis.

        Returns
        -------
        tuple
            A tuple containing:
            - A string indicating the loading status.
            - A Dash DataTable displaying the CCC analysis results.
        """
        if not n_clicks or n_clicks == 0:
            return no_update, html.P("No cell-cell communication results yet. Run the analysis to see results here.", style={"color": "#6c757d", "fontSize": "14px", "marginTop": "10px"},), "", ""
        
        adata = get_working_dataset()
        if adata is None:
            return "done", "No dataset available for cell-cell communication analysis.", "", ""
        
        # Run the CCC analysis using the provided parameters
        liana_results = run_liana(adata, grouping_variable, method, resource)
        update_state_store(CCC_results={"results": liana_results})
        
        # Filter and format the results for display
        
        results_table = liana_output_table(liana_results)
        results_table = make_sortable_table(results_table, "ccc-results-table")
        summary = summarise_celltype_interactions(liana_results)

        # Network plot generation
        network_fig = create_network_plot(summary)

        fig = px.scatter(
            summary,
            x="target",
            y="source",
            size="bubble_size",
            color="bubble_color",
            hover_data=[
                "interaction_count",
                "mean_magnitude",
                "mean_specificity",
            ],
        )

        fig.update_yaxes(categoryorder="category ascending")
        fig.update_layout(
            title="Cell-Cell Communication Bubble Plot",
        )
        
        return "done", results_table, dcc.Graph(figure=fig), dcc.Graph(figure=network_fig)
    
    @app.callback(
        Output("ccc-summary-container", "children", allow_duplicate=True),
        Output("ccc-bubble-plot-container", "children", allow_duplicate=True),
        Output("ccc-network-plot-container", "children", allow_duplicate=True),
        Input("ccc-apply-filters-button", "n_clicks"),
        State("ccc-source-filter-dropdown", "value"),
        State("ccc-target-filter-dropdown", "value"),
        State("ccc-interaction-filter-input", "value"),
        State("ccc-show-network-labels", "value"),
        prevent_initial_call=True,
    )
    def apply_liana_filters(n_clicks, source_filter, target_filter, interaction_filter, show_labels_value):
        """
        Filters the LIANA results based on user-selected criteria.

        Parameters
        ----------
        n_clicks : int
            Number of times the "Apply Filters" button has been clicked.
        source_filter : str
            The selected source cell type for filtering.
        target_filter : str
            The selected target cell type for filtering.
        interaction_filter : int
            The input number for filtering interactions.
            
        Returns
        -------
        tuple
            A tuple containing:
            - A Dash DataTable displaying the filtered LIANA results.
            - A Dash Graph displaying the filtered bubble plot.
        """
        if not n_clicks or n_clicks == 0:
            return no_update, no_update, no_update
        
        history = get_state_store()
        liana_results = history.get("CCC_results", {}).get("results")

        if liana_results is None:
            logger.warning("No LIANA results found in state store for filtering.")
            return html.P("No cell-cell communication results available to filter.", style={"color": "#6c757d", "fontSize": "14px", "marginTop": "10px"}), "", ""
        
        filtered_results = filter_liana_results(
            liana_results,
            source=source_filter if source_filter != "_all_" else None,
            target=target_filter if target_filter != "_all_" else None,
        )

        filtered_results = filtered_results.sort_values(by="magnitude_rank", ascending=True).head(interaction_filter if interaction_filter is not None else len(filtered_results))

        show_labels = True in (show_labels_value or [])
        network_fig = create_network_plot(summarise_celltype_interactions(filtered_results), show_labels=show_labels)

        filtered_results["interaction"] = (
            filtered_results["ligand_complex"]
            + " → "
            + filtered_results["receptor_complex"]
        )

        results_table = liana_output_table(filtered_results)
        results_table = make_sortable_table(results_table, "ccc-results-table")
        filtered_results["bubble_size"] = 1 - filtered_results["magnitude_rank"]
        filtered_results["bubble_color"] = 1 - filtered_results["specificity_rank"]


        if target_filter == "_all_":
            fig = px.scatter(
                filtered_results,
                x="target",
                y="interaction",
                size="bubble_size",
                color="bubble_color",
                hover_data=[
                    "ligand_complex",
                    "receptor_complex",
                    "magnitude_rank",
                    "specificity_rank",
                ],
            )

            fig.update_traces(
                marker=dict(sizemode="area")
            )
            fig.update_layout(
                title="Cell-Cell Communication Bubble Plot",
                xaxis_title="Target Cell Type",
                yaxis_title="Interaction (Ligand → Receptor)",
            )
        else:
            fig = px.scatter(
                filtered_results,
                x="magnitude_rank",
                y="interaction",
                size="bubble_size",
                color="bubble_color",
                hover_data=[
                    "ligand_complex",
                    "receptor_complex",
                    "magnitude_rank",
                    "specificity_rank",
                ],
            )

            fig.update_xaxes(autorange="reversed")

            fig.update_traces(
                marker=dict(sizemode="area")
            )
            fig.update_layout(
                title="Cell-Cell Communication Bubble Plot",
                xaxis_title="Magnitude Rank (lower is stronger)",
                yaxis_title="Interaction (Ligand → Receptor)",
            )

        return results_table, dcc.Graph(figure=fig), dcc.Graph(figure=network_fig)
    
    @app.callback(
        Output("ccc-summary-container", "children", allow_duplicate=True),
        Output("ccc-bubble-plot-container", "children", allow_duplicate=True),
        Output("ccc-network-plot-container", "children", allow_duplicate=True),
        Output("ccc-show-network-labels", "value"),
        Input("ccc-reset-filters-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_liana_filters(n_clicks):
        """"
        Reset the LIANA results filters and restore the original unfiltered results.

        Parameters
        ----------
        n_clicks : int
            Number of times the "Reset Filters" button has been clicked.
        
        Returns
        -------

        """
        if not n_clicks or n_clicks == 0:
            return no_update, no_update, no_update, no_update
        
        history = get_state_store()
        liana_results = history.get("CCC_results", {}).get("results")

        if liana_results is None:
            logger.warning("No LIANA results found in state store for filtering.")
            return html.P("No cell-cell communication results available to filter.", style={"color": "#6c757d", "fontSize": "14px", "marginTop": "10px"}), "", "", [True]
        
        results_table = liana_output_table(liana_results)
        results_table = make_sortable_table(results_table, "ccc-results-table")
        summary = summarise_celltype_interactions(liana_results)

        network_fig = create_network_plot(summary, show_labels=True)

        fig = px.scatter(
            summary,
            x="target",
            y="source",
            size="bubble_size",
            color="bubble_color",
            hover_data=[
                "interaction_count",
                "mean_magnitude",
                "mean_specificity",
            ],
        )

        fig.update_yaxes(categoryorder="category ascending")
        fig.update_layout(
            title="Cell-Cell Communication Bubble Plot",
        )

        return results_table, dcc.Graph(figure=fig), dcc.Graph(figure=network_fig), [True]


