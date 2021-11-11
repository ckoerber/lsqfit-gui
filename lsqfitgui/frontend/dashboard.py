"""Provides dashboard for lsqfitgui."""
from typing import Optional, Dict, Any, Callable, List
from os import path

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
    EXPORT_PRIOR_CALLBACK,
)

from lsqfitgui.frontend.content import get_content
from lsqfitgui.frontend.content import FCN_SOURCE_CALLBACK, DEFAULT_PLOTS  # noqa


def get_layout(
    fit: nonlinear_fit,
    name: str = "Lsqfit GUI",
    meta_config: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable[[nonlinear_fit], html.Base]] = None,
    plots: Optional[List[Dict[str, Any]]] = None,
    tex_function: bool = True,
) -> html.Div:
    """Create sidebar and content given fit and config values.

    Arguments:
        fit: The lsqfit object which should be rendered.
        meta_config: Meta information for the sidebar setup.
        meta_values: Current values of the meta configuration.
        use_default_content: Render default GUI elements or not.
        get_additional_content: Function to return additional html content given a fit.
            This should be used for customizations.
        tex_function: Try to display latex expression for fit function.
    """
    sidebar = get_sidebar(fit.prior, meta_config=meta_config, meta=meta)
    sidebar.className = "sticky-top bg-light p-4"

    content = (
        get_content(fit, name=name, plots=plots, tex_function=tex_function)
        if use_default_content
        else None
    )
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
ASSETS = path.abspath(path.join(path.dirname(path.dirname(__file__)), "assets"))

UPDATE_LAYOUT_CALLBACK_ARGS = (
    Output("body", "children"),
    [
        Input(*SIDEBAR_PRIOR_IDS_INPUT),
        Input(*SIDEBAR_PRIOR_VALUES_INPUT),
        Input(*SIDEBAR_META_INPUT),
    ],
)
