from dash import Input, Output, State, html, no_update, dash_table, dcc
import dash_bootstrap_components as dbc
from viral_platform.analysis.viral_gene_detection import find_viral_genes, find_custom_viral_genes
from viral_platform.state.dataset_store import update_state_store

def help_icon():
    return html.Span(
        "?",
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "justifyContent": "center",
            "width": "18px",
            "height": "18px",
            "borderRadius": "50%",
            "border": "1.5px solid #6c757d",
            "fontSize": "11px",
            "color": "#6c757d",
            "cursor": "pointer",
            "marginLeft": "6px",
            "verticalAlign": "middle",
        },
    )


# ── Virus cards ────────────────────────────────────────────────────────
def virus_card(icon_char, name, badge_text, detail):
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        icon_char,
                        style={
                            "fontSize": "28px",
                            "marginRight": "12px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.A(name, href="#", style={"fontWeight": "600", "color": "#0d6efd", "textDecoration": "none"}),
                                    dbc.Badge(
                                        badge_text,
                                        color="secondary",
                                        style={"marginLeft": "8px", "fontSize": "11px"},
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            html.P(detail, style={"margin": "2px 0 0", "fontSize": "13px", "color": "#6c757d"}),
                        ]
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
        ],
        style={
            "padding": "12px 16px",
            "borderRight": "1px solid #dee2e6",
            "flex": "1",
        },
    )


# Detection Results
def create_viral_gene_detection_results(pass_fail, color, gene_count_per_virus, detected_features, all_genes, unique_count, not_found=None):
    return html.Div(
                [
                    # Header row
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span(
                                            f"{pass_fail}",
                                            style={
                                                "display": "inline-flex",
                                                "alignItems": "center",
                                                "justifyContent": "center",
                                                "width": "22px",
                                                "height": "22px",
                                                "borderRadius": "50%",
                                                "backgroundColor": f"{color}",
                                                "color": "#fff",
                                                "fontWeight": "700",
                                                "fontSize": "13px",
                                                "marginRight": "8px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Detection Results", style={"fontWeight": "600", "fontSize": "20px"}),
                                            ]
                                        ),
                                    ],
                                    style={"display": "flex", "alignItems": "center"},
                                ),
                            ),
                        ],
                    ),
                    html.P("Detected Viral Genes in Dataset", style={"fontWeight": "600", "marginBottom": "10px"}),

                    html.Div(
                        [
                            # virus_card("🔷", "Epstein–Barr virus (EBV)", "89 genes", "Matched 89 of 182 known genes (48.9%)"),
                            # virus_card("🔵", "Human herpesvirus 6 (HHV-6)", "12 genes", "Matched 12 of 162 known genes (7.4%)"),
                            *[virus_card(
                                "🔷",
                                virus,
                                f"{count} genes",
                                html.Span(
                                    [
                                        f"Matched {count} of {len(all_genes)} genes found ({(count/len(all_genes))*100:.1f}%)",
                                        html.Br(),
                                        f"{len(detected_features)} features detected",
                                    ]
                                ),
                            ) for virus, count in gene_count_per_virus.items()],
                            html.Div(
                                [
                                    html.P(
                                        "Total unique viral genes detected",
                                        style={"fontSize": "12px", "color": "#6c757d", "margin": "0 0 2px"},
                                    ),
                                    html.Span(f"{unique_count}", style={"fontSize": "32px", "fontWeight": "700", "color": "#198754"}),
                                ],
                                style={"padding": "12px 16px", "textAlign": "center", "flex": "0 0 auto"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "border": "1px solid #dee2e6",
                            "borderRadius": "6px",
                            "backgroundColor": "#fff",
                            "marginBottom": "12px",
                        },
                    ),

                    # Detected Genes Collapsible
                    html.Div([
                        dbc.Accordion([
                            dbc.AccordionItem([
                                html.P(", ".join(map(str, all_genes)), style={"fontSize": "13px", "color": "#6c757d", "whiteSpace": "pre-wrap"}),
                            ],
                            title="Detected Genes" + (f", {len(not_found)}" if not_found else "")),
                        ])
                    ],
                        style={
                            "backgroundColor": "#fff",
                            "border": "1px solid #dee2e6",
                            "borderRadius": "8px",
                            "padding": "16px",
                            "marginBottom": "16px",
                        },
                    ),

                    # ── 5. Add/Append Viral Genes ─────────────────────────────────
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.Span("Add/Append Viral Genes", style={"fontWeight": "600"}),
                                            html.Span(" (Optional)", style={"color": "#6c757d"}),
                                            help_icon(),
                                        ],
                                        style={"display": "flex", "alignItems": "center", "gap": "4px", "marginBottom": "4px"},
                                    ),
                                    html.P(
                                        "Add additional viral genes that may not be in our database.",
                                        style={"fontSize": "12px", "color": "#6c757d", "margin": "0"},
                                    ),
                                ],
                                width=3,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="append-viral-genes-input",
                                    placeholder="Enter gene names separated by commas or new lines",
                                    type="text",
                                ),
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "+ Add Genes",
                                    id="append-viral-genes-button",
                                    color="primary",
                                    outline=True,
                                    size="sm",
                                    style={"whiteSpace": "nowrap"},
                                ),
                                width="auto",
                                style={"display": "flex", "alignItems": "center"},
                            ),
                        ],
                        align="center",
                        style={
                            "backgroundColor": "#fff",
                            "border": "1px solid #dee2e6",
                            "borderRadius": "8px",
                            "padding": "12px 16px",
                            "marginBottom": "16px",
                        },
                    ),
                ],
            )

def register_vd_callbacks(app):
    @app.callback(
        Output("custom-detection-card", "style"),
        Output("custom-detection-card-title", "style"),
        Output("custom-gene-list-container", "hidden"),
        Input("detection-method-radio", "value"),
    )
    def update_custom_card_style(selected_method):
        if selected_method == "custom":
            return {
                "border": "2px solid #0d6efd",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#f0f6ff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#0d6efd"}, False
        else:
            return {
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#ffffff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#212529"}, True
    
    @app.callback(
        Output("automatic-detection-card", "style"),
        Output("automatic-detection-card-title", "style"),
        Input("detection-method-radio", "value"),
    )
    def update_automatic_card_style(selected_method):
        if selected_method == "automatic":
            return {
                "border": "2px solid #0d6efd",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#f0f6ff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#0d6efd"}
        else:
            return {
                "border": "2px solid #dee2e6",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "backgroundColor": "#ffffff",
                "cursor": "pointer",
            }, {"fontWeight": "600", "color": "#212529"}
    
    @app.callback(
        Output("viral-gene-detection-loading-signal", "children"),
        Output("viral-gene-detection-results-container", "children"),
        Input("run-viral-gene-detection-button", "n_clicks"),
        State("detection-method-radio", "value"),
        State("custom-gene-list-input", "value"),
        State("virus-select-dropdown", "value"),
    )
    def run_viral_gene_detection(n_clicks, selected_method, custom_gene_list, selected_virus):
        if n_clicks is None or n_clicks == 0:
            return no_update, "No viral gene detection results yet. Run the detection to see results here."
        
        if selected_method == "automatic":
            detected_genes = find_viral_genes(selected_virus)
            print(detected_genes)
            gene_count_per_virus = {}
            all_genes = []
            detected_features = []
            for key, value in detected_genes.items():
                if value["features"] == [] and value["genes"] == []:
                    continue
                gene_count_per_virus[key] = len(value["genes"])
                all_genes.extend(value["genes"])
                detected_features.extend(value["features"])
            unique_count = sum(gene_count_per_virus.values())
            # Update the state store with detected viral genes and features
            update_state_store(viral_detection={
                "viral_genes": ", ".join(map(str, all_genes)),
                "viral_features": ", ".join(map(str, detected_features)),
            })
            if len(all_genes) > 0:
                return f"Automatic detection completed", create_viral_gene_detection_results('✓', '#198754', gene_count_per_virus, detected_features, all_genes, unique_count)
            else:
                return f"Automatic detection completed, but no viral genes were detected.", create_viral_gene_detection_results('✗', '#dc3545', gene_count_per_virus, detected_features, all_genes, unique_count)
        elif selected_method == "custom":
            detected_genes = find_custom_viral_genes(custom_gene_list)
            print(detected_genes)
            gene_count_per_virus = {}
            all_genes = []
            not_found = []
            detected_features = []
            for key, value in detected_genes.items():
                if detected_genes["features"] == [] and detected_genes["genes"] == []:
                    continue
                gene_count_per_virus["Custom List"] = len(detected_genes["genes"])
                all_genes.extend(detected_genes["genes"])
                detected_features.extend(detected_genes["features"])
            if detected_genes["not_found"] != []:
                not_found.extend(detected_genes["not_found"])
            else:
                not_found = None
            unique_count = sum(gene_count_per_virus.values())
            # Update the state store with detected viral genes and features
            update_state_store(viral_detection={
                "viral_genes": ", ".join(map(str, all_genes)),
                "viral_features": ", ".join(map(str, detected_features)),
            })
            if len(all_genes) > 0:
                return f"Custom detection completed", create_viral_gene_detection_results('✓', '#198754', gene_count_per_virus, detected_features, all_genes, unique_count, not_found)
            else:
                return f"Custom detection completed, but no viral genes were detected.", create_viral_gene_detection_results('✗', '#dc3545', gene_count_per_virus, detected_features, all_genes, unique_count, not_found)