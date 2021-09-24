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
    sidebar.className = "sticky-top bg-light p-4"
    content.className = "col-xs-12 col-sm-7 col-md-8 col-xl-9 col-xxl-10"
    layout = html.Div(
        children=html.Div(
            children=[
                html.Div(
                    children=sidebar,
                    className="col-xs-12 col-sm-5 col-md-4 col-xl-3 col-xxl-2",
                    id="sticky-sidebar",
                ),
                content,
            ],
            className="row py-3",
        ),
        className="container-fluid",
    )

    return layout


EXTERNAL_STYLESHEETS = [BOOTSTRAP]
DASHBOARD_FORM_INPUT = SIDEBAR_FORM_INPUT
