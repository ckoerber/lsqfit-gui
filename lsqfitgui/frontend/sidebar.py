"""Sidebar definitions for dash app."""
from typing import Dict, Optional

from gvar import GVar

from dash import html, dcc
from dash.dependencies import ALL

from numpy import concatenate

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


def get_sidebar(
    elements: Dict[str, GVar],
    meta_config: Optional[Dict] = None,
    meta_values: Optional[Dict] = None,
):

    """Create sidebar."""
    if meta_config is not None:
        meta_elements = [html.H4("Meta")]
        for config in meta_config:
            config = config.copy()
            name = config.pop("name")
            config["debounce"] = True
            config["className"] = "form-control-sm"
            config["id"] = {"type": "meta", "index": name}
            config["value"] = meta_values[name]
            meta_elements.append(
                dbc.FormGroup(
                    [
                        dbc.Label(name, html_for=f"input-meta-{name}", width=4),
                        dbc.Col(dbc.Input(**config), width=8),
                    ],
                    row=True,
                )
            )
        meta_elements.append(html.Hr())
    else:
        meta_elements = []

    names = concatenate([
        [n+' '+str(k) for k in range(len(elements[n]))] if hasattr(elements[n], '__len__') else [n]
        for n in elements
    ])
    gvars = elements.flatten()
    elements = dict(zip(names, gvars))

    return html.Div(
        children=meta_elements
        + [
            html.H4("Priors"),
            dbc.Form(
                dbc.Table(
                    [
                        html.Thead(
                            html.Tr([html.Th("name"), html.Th("mean"), html.Th("sdev")])
                        )
                    ]
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
            html.Hr(),
            html.Div(
                [
                    html.Button(
                        "Save fit",
                        id="save-fit-btn",
                        className="btn btn-outline-success",
                    ),
                    dcc.Download(id="save-fit"),
                ],
                className="text-right",
            ),
        ],
        style=SIDEBAR_STYLE,
    )


SIDEBAR_PRIOR_INPUT = ({"type": "prior", "index": ALL}, "value")
SIDEBAR_META_INPUT = ({"type": "meta", "index": ALL}, "value")


SAVE_FIT_INPUT = ("save-fit-btn", "n_clicks")
SAVE_FIT_OUTPUT = ("save-fit", "data")
