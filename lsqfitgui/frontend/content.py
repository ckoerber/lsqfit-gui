""""""
from dash import html, dcc

import dash_bootstrap_components as dbc

from lsqfitgui.plot.fit import plot_fit, plot_residuals


def get_content(fit, name: str = "Lsqfit GUI"):

    fig_fit = plot_fit(fit)
    fig_residuals = plot_residuals(fit)
    content = html.Div(
        children=[
            html.H1(children=name),
            dbc.Tabs(
                [
                    dbc.Tab(
                        children=html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.H2(children="Fit"),
                                        dcc.Graph(figure=fig_fit),
                                    ],
                                    className="col-lg-8",
                                ),
                                html.Div(
                                    children=[
                                        html.H2(children="Details"),
                                        html.Pre(children=fit.format(maxline=True)),
                                    ],
                                    className="col-lg-4",
                                ),
                            ],
                            className="row",
                        ),
                        label="Details",
                        tab_id="details",
                    ),
                    dbc.Tab(
                        children=[html.H2(children="Fit"), dcc.Graph(figure=fig_fit)],
                        label="Fit",
                        tab_id="fit",
                    ),
                    dbc.Tab(
                        children=[
                            html.H2(children="Residuals"),
                            dcc.Graph(figure=fig_residuals),
                        ],
                        label="Residuals",
                        tab_id="residuals",
                    ),
                ],
                active_tab="details",
            ),
        ]
    )
    return content
