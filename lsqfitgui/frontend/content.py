"""Submodule providing GUI content."""
from dash import html, dcc

from lsqfitgui.plot.fit import plot_fit, plot_residuals
from lsqfitgui.util.function import document_function


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
                        html.Pre(document_function(fit.fcn)),
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
