"""Provides dashboard for lsqfitgui."""
from typing import Optional, Dict, Any
from dash import html
from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfitgui.frontend.sidebar import (
    get_sidebar,
    SIDEBAR_PRIOR_INPUT,
    SIDEBAR_META_INPUT,
)
from lsqfitgui.frontend.content import get_content
from lsqfitgui.backend.sidebar import process_priors


def get_layout(fit, meta_config: Optional[Dict[str, Any]] = None, **kwargs):
    """Stuf...
    """
    sidebar = get_sidebar(fit.prior, meta_config=meta_config)
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
DASHBOARD_PRIOR_INPUT = SIDEBAR_PRIOR_INPUT
DASHBOARD_META_INPUT = SIDEBAR_META_INPUT


def update_layout(
    inp, initial_fit, meta_config: Optional[Dict[str, Any]] = None, **kwargs
):
    """Parses form input values to create new layout."""
    new_fit = process_priors(inp, initial_fit)
    return get_layout(new_fit, meta_config=meta_config)
