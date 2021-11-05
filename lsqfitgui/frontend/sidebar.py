"""Sidebar definitions for dash app."""
from typing import Dict, Optional

from gvar import GVar

from dash import html, dcc
from dash.dependencies import ALL, Input, Output

import dash_bootstrap_components as dbc

from lsqfitgui.frontend.widgets.export_prior import (  # noqa
    get_export_prior_widget,
    EXPORT_PRIOR_CALLBACK_ARGS,
    toggle_prior_widget,
)

SIDEBAR_STYLE = {"overflow-y": "auto", "height": "100vh"}


def get_float_widget(
    name: str, value: float, input_only: bool = False, **kwargs
) -> dbc.Row:
    """Create form group for float input."""
    inp = dbc.Input(
        type="number",
        id={"type": "prior", "name": name},
        placeholder=name,
        value=str(value),
        className="form-control-sm",
        debounce=True,
        **kwargs,
    )
    return (
        inp
        if input_only
        else dbc.Row(
            [dbc.Col(dbc.Label(name, html_for=f"input-prior-{name}")), dbc.Col(inp)],
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
            config["id"] = {"type": "meta", "name": name}
            config["value"] = meta_values[name]

            if "options" in config:
                inp = dbc.Select(**config)
            else:
                config["className"] = "form-control-sm"
                config["debounce"] = True
                config["placeholder"] = name
                inp = dbc.Input(**config)

            meta_elements.append(
                dbc.Row(
                    [
                        dbc.Col(dbc.Label(name, html_for=f"input-meta-{name}")),
                        dbc.Col(inp),
                    ],
                )
            )
        meta_elements.append(html.Hr())
    else:
        meta_elements = []

    table_rows = []
    for key, val in elements.items():
        if hasattr(val, "__len__"):
            table_rows.append(html.Tr([html.Td(html.B(key), colSpan=3)]))
            for n, dist in enumerate(val):
                name = f"{key}__array_{n}"
                row_content = [
                    html.Td(
                        dbc.Label(html.Small(n), html_for=f"input-prior-{name}"),
                        className="ps-4",
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
                    get_export_prior_widget(elements),
                    html.Span(
                        [
                            html.Button(
                                "Save fit",
                                id="save-fit-btn",
                                className="btn btn-outline-success",
                            ),
                            dcc.Download(id="save-fit"),
                        ],
                        className="ms-2",
                    ),
                ],
                className="text-end",
            ),
        ],
        style=SIDEBAR_STYLE,
    )


SIDEBAR_PRIOR_IDS_INPUT = ({"type": "prior", "name": ALL}, "id")
SIDEBAR_PRIOR_VALUES_INPUT = ({"type": "prior", "name": ALL}, "value")
SIDEBAR_META_INPUT = ({"type": "meta", "name": ALL}, "value")

SAVE_FIT_CALLBACK_ARGS = (
    Output("save-fit", "data"),
    [Input("save-fit-btn", "n_clicks")],
)
