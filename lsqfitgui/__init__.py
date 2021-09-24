"""Lsqfit GUI."""
from dash import Dash, html
from dash.dependencies import Input, Output

from lsqfitgui.frontend.dashboard import (
    get_layout,
    update_layout,
    EXTERNAL_STYLESHEETS,
    DASHBOARD_FORM_INPUT,
)


def run_server(fit, name: str = "Lsqfit GUI", debug: bool = True, **kwargs):
    """Provide dashboard for lsqfitgui."""
    app = Dash(name, external_stylesheets=EXTERNAL_STYLESHEETS)
    app.layout = html.Div(children=get_layout(fit, **kwargs), id="body")

    @app.callback(
        Output("body", "children"), Input(*DASHBOARD_FORM_INPUT),
    )
    def display_output(inp):
        return update_layout(inp, initial_fit=fit)

    app.run_server(debug=debug)
