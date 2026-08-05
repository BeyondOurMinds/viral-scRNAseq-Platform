from dash import html, register_page

from viral_platform.layout.DifferentialExpression_panel import create_differential_expression_panel


register_page(__name__, path="/differential-expression", name="DE Analysis", order=5)


def layout():
    return html.Div(className="module-page", children=[create_differential_expression_panel()])
