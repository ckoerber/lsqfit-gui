"""Provides dashboard for lsqfitgui."""
from typing import Optional, Dict, Any, Callable
from dash import html
from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfitgui.frontend.sidebar import (
    get_sidebar,
    SIDEBAR_PRIOR_INPUT,
    SIDEBAR_META_INPUT,
)
from lsqfitgui.frontend.content import get_content
from lsqfitgui.backend.sidebar import process_priors, process_meta


def get_layout(
    fit,
    meta_config: Optional[Dict[str, Any]] = None,
    meta_values: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable] = None,
    **kwargs,
):
    """Stuf...
    """
    sidebar = get_sidebar(fit.prior, meta_config=meta_config, meta_values=meta_values)
    sidebar.className = "sticky-top bg-light p-4"

    content = get_content(fit) if use_default_content else None
    additional_content = get_additional_content(fit) if get_additional_content else None

    layout = html.Div(
        children=html.Div(
            children=[
                html.Div(
                    children=sidebar,
                    className="col-xs-12 col-sm-5 col-md-4 col-xl-3 col-xxl-2",
                    id="sticky-sidebar",
                ),
                html.Div(
                    children=[content, additional_content],
                    className="col-xs-12 col-sm-7 col-md-8 col-xl-9 col-xxl-10",
                ),
            ],
            className="row py-3",
        ),
        className="container-fluid",
    )

    return layout


EXTERNAL_STYLESHEETS = [BOOTSTRAP]
DASHBOARD_PRIOR_INPUT = SIDEBAR_PRIOR_INPUT
DASHBOARD_META_INPUT = SIDEBAR_META_INPUT


def update_layout_from_prior(
    prior,
    initial_fit,
    setup: Optional[Dict[str, Any]] = None,
    meta_config: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable] = None,
    **kwargs,
):
    """Parses form input values to create new layout."""
    setup = process_meta(setup, meta_config) if setup else None
    new_fit = process_priors(prior, initial_fit)
    return (
        get_layout(
            new_fit,
            meta_config=meta_config,
            meta_values=setup,
            use_default_content=use_default_content,
            get_additional_content=get_additional_content,
        ),
        new_fit,
    )


def update_layout_from_meta(
    inp,
    fit_setup_function,
    fit_setup_kwargs,
    meta_config: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable] = None,
    **kwargs,
):
    """Parses form input values to create new layout."""
    setup = process_meta(inp, meta_config)
    setup = {key: setup.get(key) or val for key, val in fit_setup_kwargs.items()}
    new_fit = fit_setup_function(**setup)
    return (
        get_layout(
            new_fit,
            meta_config=meta_config,
            use_default_content=use_default_content,
            get_additional_content=get_additional_content,
            meta_values=setup,
        ),
        new_fit,
    )
