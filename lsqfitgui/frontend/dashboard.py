"""Provides dashboard for lsqfitgui."""
from typing import Optional, Dict, Any, Callable

from dash import html
from dash.dependencies import Input, Output

from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfit import nonlinear_fit

from lsqfitgui.frontend.sidebar import (
    get_sidebar,
    SIDEBAR_PRIOR_IDS_INPUT,
    SIDEBAR_PRIOR_VALUES_INPUT,
    SIDEBAR_META_INPUT,
)
from lsqfitgui.frontend.sidebar import (  # noqa
    SAVE_FIT_CALLBACK_ARGS,
    EXPORT_PRIOR_CALLBACK_ARGS,
    toggle_prior_widget,
)

from lsqfitgui.frontend.content import get_content
from lsqfitgui.frontend.content import FCN_SOURCE_CALLBACK  # noqa
from lsqfitgui.backend.sidebar import process_priors, process_meta


def get_layout(
    fit: nonlinear_fit,
    name: str = "Lsqfit GUI",
    meta_config: Optional[Dict[str, Any]] = None,
    meta_values: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable[[nonlinear_fit], html.Base]] = None,
    fcns = {}, # add type hint later
    **kwargs,
) -> html.Div:
    """Create sidebar and content given fit and config values.

    Arguments:
        fit: The lsqfit object which should be rendered.
        meta_config: Meta information for the sidebar setup.
        meta_values: Current values of the meta configuration.
        use_default_content: Render default GUI elements or not.
        get_additional_content: Function to return additional html content given a fit.
            This should be used for customizations.
    """
    sidebar = get_sidebar(fit.prior, meta_config=meta_config, meta_values=meta_values)
    sidebar.className = "sticky-top bg-light p-4"

    content = get_content(fit, name=name, fcns=fcns) if use_default_content else None
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


EXTERNAL_STYLESHEETS = [
    BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/katex@0.13.18/dist/katex.min.css",
]
MATHJAX_CDN = (
    "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js"
    "?config=TeX-MML-AM_CHTML"
)


EXTERNAL_SCRIPTS = [{"type": "text/javascript", "src": MATHJAX_CDN}]

UPDATE_LAYOUT_CALLBACK_ARGS = (
    Output("body", "children"),
    [
        Input(*SIDEBAR_PRIOR_IDS_INPUT),
        Input(*SIDEBAR_PRIOR_VALUES_INPUT),
        Input(*SIDEBAR_META_INPUT),
    ],
)


def update_layout_from_prior(
    prior,
    initial_fit,
    name: str = "Lsqfit GUI",
    setup: Optional[Dict[str, Any]] = None,
    meta_config: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable] = None,
    **kwargs,
):
    """Parse prior form input values to create new layout.

    Creates new fit object for new prior and calls get_layout.
    """
    setup = process_meta(setup, meta_config) if setup else None
    new_fit = process_priors(prior, initial_fit)
    return (
        get_layout(
            new_fit,
            name=name,
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
    name: str = "Lsqfit GUI",
    meta_config: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable] = None,
    **kwargs,
):
    """Parse meta form input values to create new layout.

    Creates new fit object for new meta data and prior (using fit_setup_function)
    and calls get_layout.
    """
    setup = process_meta(inp, meta_config)
    setup = {key: setup.get(key) or val for key, val in fit_setup_kwargs.items()}
    new_fit = fit_setup_function(**setup)
    return (
        get_layout(
            new_fit,
            name=name,
            meta_config=meta_config,
            use_default_content=use_default_content,
            get_additional_content=get_additional_content,
            meta_values=setup,
        ),
        new_fit,
    )
