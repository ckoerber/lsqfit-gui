"""Lsqfit GUI."""
from dash import Dash, html
from dash.dependencies import Input, Output

import numpy as np
import gvar as gv
from lsqfit import nonlinear_fit

from lsqfitgui.frontend.dashboard import (
    get_layout,
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
    def display_output(prior_values):
        prior_values = np.array(prior_values, dtype=float).reshape(
            len(prior_values) // 2, 2
        )
        print(prior_values)
        prior = {
            key: val
            for key, val in zip(fit.p, gv.gvar(prior_values[:, 0], prior_values[:, 1]))
        }
        print(prior)
        new_fit = nonlinear_fit(fit.data, fit.fcn, prior)
        return get_layout(new_fit)

    app.run_server(debug=debug)
