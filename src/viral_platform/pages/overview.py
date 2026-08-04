from dash import html, register_page


register_page(__name__, path="/", name="Overview", order=0)


def layout():
    """Landing page shown at the root route."""
    return html.Div(
        className="module-page",
        children=[
            html.Div(
                className="module-panel",
                children=[
                    html.H2("Overview"),
                    html.P(
                        "Use the left navigation to move between upload and analysis modules. "
                        "Each module is routed as its own Dash page."
                    ),
                ],
            )
        ],
    )
