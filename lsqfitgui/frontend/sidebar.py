"""Sidebar definitions for dash app."""
from typing import Dict, Optional, List, Any

from gvar import GVar

from dash import html, dcc
from dash.dependencies import ALL, Input, Output

import dash_bootstrap_components as dbc

from lsqfitgui.util.callback import CallbackWrapper
from lsqfitgui.frontend.widgets.export_prior import (
    get_export_prior_widget,
    EXPORT_PRIOR_CALLBACK,
)


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


class Sidebar:
    """Sidebar template class which creates forms for prior values and meta configs."""

    update_callback_inputs = [
        Input({"type": "prior", "name": ALL}, "id"),
        Input({"type": "prior", "name": ALL}, "value"),
        Input({"type": "meta", "name": ALL}, "value"),
    ]
    """Callback input arguments when changing sidebar forms."""

    save_fit_callback_args = (
        Output("save-fit", "data"),
        [Input("save-fit-btn", "n_clicks")],
    )
    """Callback arguments for saving a fit to file."""

    export_prior_callback: CallbackWrapper = EXPORT_PRIOR_CALLBACK
    """Callback for exporting a prior to clipboard."""

    style: Dict[str, str] = {"overflow-y": "auto", "height": "100vh"}
    """HTML style of sidebar."""
    className: str = "sticky-top bg-light p-4"
    """HTML class name of sidebar."""

    def __init__(
        self, meta_config: Optional[List[Dict[str, Any]]] = None,
    ):
        """Initialize sidebar by setting private attributes.

        Arguments:
            meta_config: Configuration to setup meta forms for fit.
        """
        self._meta: Dict[str, Any] = {}
        self._prior: Dict[str, GVar] = {}
        self._layout: Optional[html.Div] = None
        self._meta_config: List[Dict[str, Any]] = meta_config or []

    @property
    def meta_config(self) -> Optional[Dict]:
        """Return current meta config."""
        return self._meta_config

    @property
    def prior(self) -> Dict[str, GVar]:
        """Return current prior."""
        return self._prior

    @property
    def layout(self) -> html.Div:
        """Return current HTML layout.

        This property is lazy loaded: it will call :meth:`Sidebar.get_sidebar` if not yet computed.
        """
        if self._layout is None:
            self._layout = self.get_sidebar(self._prior, self._meta)
        return self._layout

    def update(self, prior: Dict[str, GVar], meta: Optional[Dict] = None) -> html.Div:
        """Update the current layout with new prior and or meta values."""
        if meta:
            self._meta = meta
        if prior:
            self._prior = prior
        self._layout = self.get_sidebar(self._prior, self._meta)
        return self._layout

    def get_sidebar(
        self, prior: Dict[str, GVar], meta: Optional[Dict[str, Any]] = None,
    ) -> html.Div:
        """Create sidebar."""
        if self.meta_config is not None:
            assert isinstance(meta, dict)
            meta_elements = [html.H4("Meta")]
            for config in self.meta_config:
                config = config.copy()
                name = config.pop("name")
                config["id"] = {"type": "meta", "name": name}
                config["value"] = meta[name]

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
        for key, val in prior.items():
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
                    html.Td(
                        get_float_widget(f"{name}-mean", dist.mean, input_only=True)
                    ),
                    html.Td(
                        get_float_widget(f"{name}-sdev", dist.sdev, input_only=True)
                    ),
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
                                html.Tr(
                                    [html.Th("name"), html.Th("mean"), html.Th("sdev")]
                                )
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
                        get_export_prior_widget(prior),
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
            style=self.style,
            className=self.className,
        )
