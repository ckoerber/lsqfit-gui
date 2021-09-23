"""Provides dashboard for lsqfitgui."""
from dash import html
from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfitgui.frontend.sidebar import get_sidebar


def get_layout(fit, **kwargs):
    """Stuf...
    """
    sidebar = get_sidebar(fit.p)
    content = html.Div(children=html.H1(children="Hello World!"), className="")
    sidebar.className = "col-xs-12 col-sm-3 col-md-3 col-lg-4"
    content.className = "col-xs-12 col-sm-9 col-md-9 col-lg-8"
    layout = html.Div(
        children=html.Div(children=[sidebar, content], className="row"),
        className="container-fluid",
    )

    return layout


EXTERNAL_STYLESHEETS = [BOOTSTRAP]
