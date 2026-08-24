import logging

from dash import Input, Output, html
from dash.exceptions import PreventUpdate

from viral_platform.io.session_saves import (
    create_export_bundle,
)


logger = logging.getLogger(__name__)


def register_save_callbacks(app):

    @app.callback(
        Output(
            "header-export-status",
            "children",
        ),
        Input(
            "header-export-btn",
            "n_clicks",
        ),
        prevent_initial_call=True,
    )
    def _export_handler(n_clicks):

        if not n_clicks:
            raise PreventUpdate

        try:
            result = create_export_bundle()

        except Exception as exc:
            logger.exception(
                "Full export bundle failed."
            )

            return html.P(
                f"Export failed: {exc}",
                style={
                    "color": "#b02a37"
                },
            )

        status = result.get(
            "status"
        )

        if status == "cancelled":
            return html.P(
                result.get(
                    "message",
                    "Export cancelled.",
                ),
                style={
                    "color": "#856404"
                },
            )

        if status == "partial":
            details = [
                html.P(
                    result.get(
                        "message",
                        "Export partially completed.",
                    ),
                    style={
                        "color": "#856404"
                    },
                )
            ]

            zip_path = result.get(
                "zip_path"
            )

            if zip_path:
                details.append(
                    html.P(
                        f"ZIP saved to: {zip_path}",
                        style={
                            "color": "#856404"
                        },
                    )
                )

            return html.Div(details)

        # ---------------------------------------------------------
        # Successful export
        # ---------------------------------------------------------

        details = [
            html.P(
                "Export completed successfully.",
                style={
                    "color": "#146c43"
                },
            )
        ]

        zip_path = result.get(
            "zip_path"
        )

        h5ad_path = result.get(
            "h5ad_path"
        )

        if zip_path:
            details.append(
                html.P(
                    f"ZIP: {zip_path}",
                    style={
                        "color": "#146c43"
                    },
                )
            )

        if h5ad_path:
            details.append(
                html.P(
                    f"H5AD: {h5ad_path}",
                    style={
                        "color": "#146c43"
                    },
                )
            )

        for note in result.get(
            "notes",
            [],
        ):
            details.append(
                html.P(
                    note
                )
            )

        return html.Div(details)