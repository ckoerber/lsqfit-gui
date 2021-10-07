"""Sidebar definitions for dash app."""
from typing import Dict, Optional

from gvar import GVar

from dash import html, dcc
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
        key=name,
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

    table_rows = []
    for key, val in elements.items():
        if hasattr(val, "__len__"):
            table_rows.append(html.Tr([html.Td(html.B(key))]))
            for n, dist in enumerate(val):
                name = f"{key}__array_{n}"
                row_content = [
                    html.Td(
                        dbc.Label(html.Small(n), html_for=f"input-prior-{name}"),
                        className="pl-4",
                    ),
                    html.Td(
                        get_float_widget(f"{name}-mean", dist.mean, input_only=True)
                    ),
                    html.Td(
                        get_float_widget(f"{name}-sdev", dist.sdev, input_only=True)
                    ),
                ]
                table_rows.append(html.Tr(row_content))

        else:
            name = key
            dist = val
            row_content = [
                html.Td(dbc.Label(name, html_for=f"input-prior-{name}")),
                html.Td(get_float_widget(f"{name}-mean", dist.mean, input_only=True)),
                html.Td(get_float_widget(f"{name}-sdev", dist.sdev, input_only=True)),
            ]
            table_rows.append(html.Tr(row_content))

    return html.Div(
        children=meta_elements
        + [
            html.H4("Priors"),
            dbc.Form(
                dbc.Table(
                    [
                        html.Thead(
                            html.Tr([html.Th("name"), html.Th("mean"), html.Th("sdev")])
                        ),
                        html.Tbody(table_rows),
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


SIDEBAR_PRIOR_KEYS_INPUT = ({"type": "prior", "index": ALL}, "key")
SIDEBAR_PRIOR_VALUES_INPUT = ({"type": "prior", "index": ALL}, "value")
SIDEBAR_META_INPUT = ({"type": "meta", "index": ALL}, "value")

SAVE_FIT_INPUT = ("save-fit-btn", "n_clicks")
SAVE_FIT_OUTPUT = ("save-fit", "data")
