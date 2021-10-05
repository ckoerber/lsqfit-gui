"""Submodule providing GUI content."""
from typing import Optional, Dict, Callable, List

from dash import html, dcc

from lsqfitgui.plot.fit import plot_fit, plot_residuals
from lsqfitgui.util.function import parse_function_expression


def document_function(
    fcn: Callable, parameters: Optional[Dict] = None
) -> List[html.Base]:
    """Documents the function."""
    documentation = []
    if fcn is None:
        return None

    fcn_name = fcn.__name__ if hasattr(fcn, "__name__") and fcn.__name__ else None
    if fcn_name:
        fcn_string = "Function: `"
        fcn_string += (
            fcn.__module__ + "."
            if hasattr(fcn, "__module__") and fcn.__module__
            else ""
        )
        fcn_string += fcn_name + "`"
        documentation.append(dcc.Markdown(fcn_string))

    if parameters:
        tex = parse_function_expression(fcn, parameters)
        if tex:
            documentation.append(html.P(fr"$${tex}$$"))

    if hasattr(fcn, "__doc__") and fcn.__doc__:
        documentation.append(html.Pre(fcn.__doc__))

    return documentation


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
