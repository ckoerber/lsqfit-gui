""""""
from dash import html
import dash_core_components as components
from lsqfitgui.plot.fit import plot_fit, plot_residuals


def get_content(fit, name: str = "Lsqfit GUI"):

    fig_fit = plot_fit(fit)
    fig_residuals = plot_residuals(fit)
    content = html.Div(
        children=[
            html.H1(children=name),
            html.H2(children="Details"),
            html.Pre(children=fit.format(maxline=True)),
            html.H2(children="Fit"),
            components.Graph(figure=fig_fit),
            html.H2(children="Residuals"),
            components.Graph(figure=fig_residuals),
        ]
    )
    return content
