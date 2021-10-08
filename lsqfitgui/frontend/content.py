"""Submodule providing GUI content."""
from typing import Optional, Dict, Callable, List

from inspect import getsource

from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from lsqfitgui.plot.fit import plot_fit, plot_residuals
from lsqfitgui.util.function import parse_function_expression
from lsqfitgui.util.versions import get_entrypoint_string, get_version_string


def document_function(
    fcn: Callable, parameters: Optional[Dict] = None
) -> List[html.Base]:
    """Documents the function."""
    documentation = []
    if fcn is None:
        return None

    fcn_name = (
        fcn.__qualname__
        if hasattr(fcn, "__qualname__") and fcn.__qualname__
        else (fcn.__name__ if hasattr(fcn, "__name__") and fcn.__name__ else None)
    )
    if fcn_name:
        fcn_string = "```python\n"
        fcn_string += (
            f"from {fcn.__module__} import "
            if hasattr(fcn, "__module__") and fcn.__module__
            else ""
        )
        fcn_string += fcn_name + "\n```"
        documentation.append(dcc.Markdown(fcn_string))

    documentation.append(
        html.Pre(get_entrypoint_string() + "\n" + get_version_string())
    )

    if parameters:
        tex = parse_function_expression(fcn, parameters)
        if tex:
            documentation.append(html.P(fr"$${tex}$$"))

    if hasattr(fcn, "__doc__") and fcn.__doc__:
        documentation.append(html.Pre(html.Code(fcn.__doc__)))

    source = getsource(fcn)
    documentation.append(
        html.Div(
            [
                html.Button(
                    "Show source code",
                    className="btn btn-outline-primary btn-small",
                    id="collapse-function-source-button",
                    n_clicks=0,
                ),
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Markdown(f"```python\n{source}\n```"), className="p-4",
                        ),
                    ),
                    id="collapse-function-source",
                    is_open=False,
                ),
            ],
            className="py-4",
        )
    )

    return documentation


def toggle_function_source_collapse(n, is_open):
    """Toggles the source code of the function."""
    return not is_open if n else is_open


FCN_SOURCE_CALLBACK = toggle_function_source_collapse
FCN_SOURCE_CALLBACK.args = (
    Output("collapse-function-source", "is_open"),
    [Input("collapse-function-source-button", "n_clicks")],
    [State("collapse-function-source", "is_open")],
)


def get_content(fit, name: str = "Lsqfit GUI"):
    """Create default content block for fit object.

    This includes the plots for the data, residuals and details.
    """
    fig_fit = plot_fit(fit)
    fig_residuals = plot_residuals(fit)
    content = html.Div(
        children=[
            html.H1(children=name),
            html.Div(
                html.Div(
                    [
                        html.H4("Fit function"),
                        html.Div(document_function(fit.fcn, fit.p)),
                        html.H4("Fit parameters"),
                        html.Pre(str(fit)),
                    ],
                    className="col",
                ),
                className="row",
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        children=[dcc.Graph(figure=fig_fit)], label="Fit", value="fit",
                    ),
                    dcc.Tab(
                        children=[dcc.Graph(figure=fig_residuals)],
                        label="Residuals",
                        value="residuals",
                    ),
                    dcc.Tab(
                        children=[html.Pre(children=fit.format(maxline=True))],
                        label="Details",
                        value="details",
                    ),
                ],
                value="fit",
                persistence=True,
                persistence_type="local",
                persisted_props=["value"],
                id="content-tabs",
            ),
        ]
    )
    return content
