"""Widget for exporting priors."""
from typing import Dict

from numpy import ndarray
from gvar import GVar, gdumps, BufferDict
import json

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


def get_export_prior_widget(prior: Dict[str, GVar]) -> html.Div:
    """Create a modal which contains copyable strings for exporting the prior."""
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
                        html.Pre(
                            html.Code(
                                "prior = "
                                + json.dumps(prior, indent=4, cls=GVarEncoder)
                            ),
                            className="bg-light p-4",
                        ),
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
