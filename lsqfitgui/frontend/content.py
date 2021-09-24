""""""
from dash import html, dcc

from lsqfitgui.plot.fit import plot_fit, plot_residuals


def get_content(fit, name: str = "Lsqfit GUI"):

    fig_fit = plot_fit(fit)
    fig_residuals = plot_residuals(fit)
    content = html.Div(
        children=[
            html.H1(children=name),
            dcc.Tabs(
                [
                    dcc.Tab(
                        children=[
                            html.H2(children="Details"),
                            html.Pre(children=fit.format(maxline=True)),
                        ],
                        label="Details",
                        value="details",
                    ),
                    dcc.Tab(
                        children=[html.H2(children="Fit"), dcc.Graph(figure=fig_fit)],
                        label="Fit",
                        value="fit",
                    ),
                    dcc.Tab(
                        children=[
                            html.H2(children="Residuals"),
                            dcc.Graph(figure=fig_residuals),
                        ],
                        label="Residuals",
                        value="residuals",
                    ),
                ],
                value="details",
                persistence=True,
                persistence_type="local",
                persisted_props=["value"],
                id="content-tabs",
            ),
        ]
    )
    return content
