"""Sidebar definitions for dash app."""
from typing import Dict

from gvar import GVar

from dash import html
from dash.dependencies import ALL

import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {}


def get_float_widget(
    name: str, value: float, input_only: bool = False, **kwargs
) -> dbc.FormGroup:
    """Create form group for float input."""
    inp = dbc.Input(
        type="number",
        id={"type": "prior", "index": name},
        placeholder=name,
        value=str(value),
        className="form-control-sm",
        debounce=True,
        **kwargs,
    )
    return (
        inp
        if input_only
        else dbc.FormGroup(
            [dbc.Label(name, html_for=f"input-prior-{name}"), inp],
            className="col-xs-6 col-sm-12 col-md-6 col-xl-3 col-xxl-2",
        )
    )


def get_sidebar(elements: Dict[str, GVar], title: str = "Priors"):
    """Create sidebar."""
    return html.Div(
        children=[
            html.H4(title),
            html.Hr(),
            dbc.Form(
                dbc.Table(
                    [html.Thead([html.Th("name"), html.Th("mean"), html.Th("sdev")])]
                    + [
                        html.Tbody(
                            html.Tr(
                                [
                                    html.Td(
                                        dbc.Label(name, html_for=f"input-prior-{name}")
                                    ),
                                    html.Td(
                                        get_float_widget(
                                            f"{name}-mean", dist.mean, input_only=True
                                        )
                                    ),
                                    html.Td(
                                        get_float_widget(
                                            f"{name}-sdev", dist.sdev, input_only=True
                                        )
                                    ),
                                ]
                            )
                        )
                        for name, dist in elements.items()
                    ],
                    borderless=True,
                    responsive=False,
                    className="table-sm",
                ),
                id="prior-form",
            ),
        ],
        style=SIDEBAR_STYLE,
    )


SIDEBAR_FORM_INPUT = ({"type": "prior", "index": ALL}, "value")
