"""Widget for exporting priors."""
from typing import Dict

import json
import yaml

from numpy import ndarray
from gvar import GVar, gdumps, BufferDict

from dash import html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc


class GVarEncoder(json.JSONEncoder):
    """Custom JSON encoder for gvars."""

    def default(self, obj):
        """Provide GVar, BufferDict and Array export options."""
        if isinstance(obj, GVar):
            return str(obj)
        elif isinstance(obj, BufferDict):
            return {key: self.default(val) for key, val in obj.items()}
        elif isinstance(obj, ndarray):
            return "[" + ", ".join([str(el) for el in obj]) + "]"
        return super().default(obj)


def gv_dict_to_yaml(gv_dict, gv_as_string: bool = True):
    """Convert prior to yaml string.

    Can be loaded in by
    ```python
    prior = {key: gv.gvar(val) for key, val in yaml_loaded.items()}
    ```

    See also https://github.com/ckoerber/lsqfit-gui/issues/2#issuecomment-939055226
    """
    cast_yaml_type = str if gv_as_string else lambda el: (el.mean, el.sdev)

    output = {}
    for key, val in gv_dict.items():
        if hasattr(gv_dict[key], "__len__"):
            output[key] = [cast_yaml_type(g) for g in val]
        else:
            output[key] = cast_yaml_type(val)
    return yaml.dumps(output, default_flow_style=None, sort_keys=False)


def get_export_prior_widget(prior: Dict[str, GVar]) -> html.Div:
    """Create a modal which contains copyable strings for exporting the prior."""
    prior = dict(**prior)
    prior_json = json.dumps(prior, indent=4, cls=GVarEncoder)
    prior_gdumps = gdumps(prior, method="json")
    prior_yaml = gv_dict_to_yaml(prior)
    modal = html.Span(
        [
            html.Button(
                "Export prior",
                id="export-prior-button",
                n_clicks=0,
                className="btn btn-outline-primary",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader("Export the prior"),
                    dbc.ModalBody(
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    html.Pre(
                                        html.Code(prior_json), className="bg-light p-4",
                                    ),
                                    label="json",
                                ),
                                dbc.Tab(
                                    html.Pre(
                                        html.Code(prior_gdumps),
                                        className="bg-light p-4",
                                    ),
                                    label="gdumps",
                                ),
                                dbc.Tab(
                                    html.Pre(
                                        html.Code(prior_yaml), className="bg-light p-4",
                                    ),
                                    label="yaml",
                                ),
                            ]
                        )
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="close-prior-button",
                            className="ml-auto",
                            n_clicks=0,
                        )
                    ),
                ],
                id="prior-modal",
                is_open=False,
                size="lg",
            ),
        ]
    )

    return modal


def toggle_prior_widget(n1, n2, is_open):
    """Return modal state."""
    if n1 or n2:
        return not is_open
    return is_open


EXPORT_PRIOR_CALLBACK_ARGS = (
    Output("prior-modal", "is_open"),
    [Input("export-prior-button", "n_clicks"), Input("close-prior-button", "n_clicks")],
    [State("prior-modal", "is_open")],
)
