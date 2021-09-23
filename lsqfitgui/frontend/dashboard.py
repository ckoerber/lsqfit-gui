"""Provides dashboard for lsqfitgui."""
from dash import html
from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfitgui.frontend.sidebar import get_sidebar, SIDEBAR_FORM_INPUT
from lsqfitgui.frontend.content import get_content


def get_layout(fit, **kwargs):
    """Stuf...
    """
    sidebar = get_sidebar(fit.prior)
    content = get_content(fit)
    sidebar.className = "col-xs-12 col-sm-3 col-md-3 col-xl-4 col-xxl-2"
    content.className = "col-xs-12 col-sm-9 col-md-9 col-xl-8 col-xxl-10"
    layout = html.Div(
        children=html.Div(children=[sidebar, content], className="row"),
        className="container-fluid",
    )

    return layout


EXTERNAL_STYLESHEETS = [BOOTSTRAP]
DASHBOARD_FORM_INPUT = SIDEBAR_FORM_INPUT
