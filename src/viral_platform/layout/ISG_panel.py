from dash import dcc, html
import dash_bootstrap_components as dbc
from viral_platform.state.dataset_store import get_cached_result


def create_isg_panel():
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

	auto_card = dbc.Col(
		html.Div(
			id="automatic-isg-detection-card",
			children=[
				html.Div(
					id="automatic-isg-detection-card-title",
					children=html.Span(["Automatic Detection"]),
					style={"fontWeight": "600", "color": "#212529"},
				),
				html.P(
					"Search using built-in ISG gene sets",
					style={"fontSize": "13px", "color": "#6c757d"},
				),
			],
			style={
				"border": "2px solid #dee2e6",
				"borderRadius": "8px",
				"padding": "12px 16px",
				"backgroundColor": "#fff",
				"cursor": "pointer",
			},
		)
	)

	custom_card = dbc.Col(
		html.Div(
			id="custom-isg-detection-card",
			children=[
				html.Div(
					id="custom-isg-detection-card-title",
					children=html.Span(["Custom Detection"]),
					style={"fontWeight": "600", "color": "#212529"},
				),
				html.P(
					"Provide your own list of ISGs",
					style={"fontSize": "13px", "color": "#6c757d"},
				),
			],
			style={
				"border": "2px solid #dee2e6",
				"borderRadius": "8px",
				"padding": "12px 16px",
				"backgroundColor": "#fff",
				"cursor": "pointer",
			},
		)
	)

	return html.Div(
		style={
			"backgroundColor": "#eff7ff",
			"padding": "20px",
			"borderRadius": "5px",
			"border": "1px solid #000000",
			"margin": "0 0 20px 0",
		},
		children=[
			html.Div(
				[
					html.H4(
						["3. ISG Detection"],
						style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
					),
					html.P(
						"Automatically detect ISGs using curated ISG sets, or provide your own gene list.",
						style={"color": "#6c757d", "marginBottom": "16px", "fontSize": "14px"},
					),
				]
			),
			dbc.Row(
				[
					dbc.Col(
						[
							html.Div(
								["Detection Method", help_icon()],
								style={
									"fontWeight": "600",
									"marginBottom": "10px",
									"display": "flex",
									"alignItems": "center",
								},
							),
							dbc.Row(
								[
									dbc.Col(
										dbc.RadioItems(
											id="isg-detection-method-radio",
											options=[
												{"label": auto_card, "value": "automatic"},
												{"label": custom_card, "value": "custom"},
											],
											value="automatic",
											inline=True,
										)
									)
								]
							),
							dbc.Row(
								[
									dbc.Col(
										html.Div(
											id="custom-isg-gene-list-container",
											children=[
												dbc.Textarea(
													id="custom-isg-gene-list-input",
													placeholder="Enter custom ISG list (comma-separated)",
													wrap=True,
												)
											],
											style={"marginTop": "10px"},
											hidden=True,
										)
									)
								]
							),
						]
					),
					dbc.Col(
						[
							dbc.Row(
								[
									html.Div(
										[
											"Select ISG Set ",
											html.Span("(Optional)", style={"color": "#6c757d", "fontWeight": "400"}),
											help_icon(),
										],
										style={
											"fontWeight": "600",
											"marginBottom": "10px",
											"display": "flex",
											"alignItems": "center",
											"gap": "4px",
										},
									),
									dcc.Dropdown(
										id="isg-set-select-dropdown",
										options=[{"label": "Auto-detect (search all ISG sets)", "value": "__auto__"}],
										value="__auto__",
										clearable=False,
									),
									html.P(
										"Search all available ISG sets for matches in the dataset.",
										style={"fontSize": "12px", "color": "#6c757d", "marginTop": "6px"},
									),
								]
							),
							dbc.Row(
								[
									dbc.Button(
										"Run ISG Detection",
										id="run-isg-detection-button",
										n_clicks=0,
										color="primary",
										className="mb-3",
									)
								]
							),
						]
					),
				],
				className="mb-3",
			),
			html.Div(
				dbc.Row(
					[
						dbc.Col(
							[
								html.Span("ℹ", style={"color": "#0d6efd", "fontSize": "18px", "marginRight": "10px"}),
								html.Span(
									"Automatic detection searches your dataset gene names against curated ISG sets. "
									"You can also provide a custom ISG list.",
									style={"fontSize": "13px"},
								),
							],
							style={"display": "flex", "alignItems": "flex-start"},
						),
						
					],
					align="center",
				),
				style={
					"backgroundColor": "#deefff",
					"border": "1px solid #b6d4fe",
					"borderRadius": "6px",
					"padding": "12px 16px",
					"marginBottom": "16px",
				},
			),
			dcc.Loading(
				type="default",
				children=html.Div(id="isg-detection-loading-signal", style={"display": "none"}),
			),
			html.Div(
				id="isg-detection-results-container",
				children=get_cached_result("isg-detection-results-container", [
					html.P(
						"No ISG detection results yet. Run the detection to see results here.",
						style={"color": "#6c757d", "fontSize": "14px"},
					)
				]),
			),
			html.Div(
				id="isg-summary-container",
				children=[
					dbc.Row(
						[
							dbc.Col(
								html.Div(
									[
										html.H4(
											["3.1 ISG Summary Statistics"],
											style={"display": "inline-flex", "alignItems": "center", "marginBottom": "2px"},
										),
										html.P(
											"Calculate per-cell ISG score and summarize score statistics.",
											style={"color": "#6c757d", "marginBottom": "16px", "marginTop": "8px", "fontSize": "14px"},
										),
									]
								)
							),
							dbc.Col(
								dbc.Button(
									"Run ISG Summary Statistics",
									id="run-isg-summary-button",
									n_clicks=0,
									color="primary",
									className="mb-3",
								),
								width="auto",
							),
						]
					),
					dcc.Loading(
						type="default",
						children=html.Div(id="isg-summary-loading-signal", style={"display": "none"}),
					),
					html.Div(
						id="isg-summary-results-container",
						children=get_cached_result("isg-summary-results-container", [
							html.P(
								"No ISG summary statistics yet. Run the analysis to see results here.",
								style={"color": "#6c757d", "fontSize": "14px"},
							)
						]),
					),
				],
				style={"marginTop": "20px", "padding": "10px", "border": "1px solid #dee2e6", "borderRadius": "5px"},
			),
		],
	)
