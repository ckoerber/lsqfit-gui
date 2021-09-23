"""Sidebar definitions for dash app."""
from typing import Dict

from gvar import GVar

from dash import html
from dash.dependencies import ALL

import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "height": "100vh",
    "min-height": "100vh",
}


def get_gvar_widget(name: str, value: float) -> dbc.FormGroup:
    """
    """
    return dbc.FormGroup(
        [
            dbc.Label(name, html_for=f"input-prior-{name}"),
            dbc.Input(
                type="text",
                id={"type": "prior", "index": name},
                placeholder=name,
                value=str(value),
                className="form-control-sm",
                debounce=True,
            ),
        ],
        className="col-xs-6 col-sm-12 col-md-6 col-xl-3 col-xxl-2",
    )


def get_sidebar(elements: Dict[str, GVar], title: str = "Priors"):
    """Create sidebar."""
    return html.Div(
        children=[
            html.H4(title),
            html.Hr(),
            dbc.Row(
                [
                    get_gvar_widget(f"{name}-{kind}", value)
                    for name, dist in elements.items()
                    for kind, value in zip(["mean", "sdev"], [dist.mean, dist.sdev])
                ],
                form=True,
                id="prior-form",
            ),
        ],
        style=SIDEBAR_STYLE,
    )


SIDEBAR_FORM_INPUT = ({"type": "prior", "index": ALL}, "value")
