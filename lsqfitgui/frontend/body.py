"""Provides templates which generate the body of a lsqfitgui app.

This module provides the base class :class:`BodyTemplate` which must be used to ensure functionality.
This is a plain template which only provides the side bar and callback structure for updating priors and meta information.
Furtermore, this module adds the :class:`BodyDefaultTemplate` which inherits from :class:`BodyTemplate` but adds additional content.
"""  # noqa
from typing import Optional, Dict, Any, List
from os import path

from dash import html, dcc
from dash.dependencies import Output

from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfit import nonlinear_fit

from lsqfitgui.util.callback import CallbackWrapper
from lsqfitgui.frontend.sidebar import Sidebar
from lsqfitgui.frontend.sidebar import EXPORT_PRIOR_CALLBACK  # noqa
from lsqfitgui.frontend.content import document_function, get_figures
from lsqfitgui.frontend.content import FCN_SOURCE_CALLBACK, DEFAULT_PLOTS  # noqa


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


class BodyTemplate:
    """Base class for rendering the html body of the app.

    The default content of the app can be customized by inheriting from this class and overloading the :meth:`get_content` method.
    """  # noqa

    sidebar_div_class: str = "col-xs-12 col-sm-5 col-md-4 col-xl-3 col-xxl-2"
    content_div_class: str = "col-xs-12 col-sm-7 col-md-8 col-xl-9 col-xxl-10"

    def __init__(
        self,
        name: str = "Lsqfit GUI",
        meta_config: Optional[List[Dict[str, Any]]] = None,
    ):
        """Initialize the html body of the app."""
        self.name: str = name
        """Name of the app."""
        self._sidebar: Sidebar = Sidebar(meta_config)
        self._content: html.Div = html.Div()
        self.additional_callbacks: List[CallbackWrapper] = []

        self.update_callback_args = (
            Output("body", "children"),
            self.sidebar.update_callback_inputs,
        )

    @property
    def sidebar(self) -> Sidebar:
        """Returns the sidebar of the app."""
        return self._sidebar

    @property
    def content(self) -> html.Div:
        """Returns current html content of the app (i.e., everything which is not the sidebar)."""
        return self._content

    @property
    def layout(self) -> html.Div:
        """Returns body layout which combines the sidebar and content."""
        return html.Div(
            html.Div(
                children=html.Div(
                    children=[
                        html.Div(
                            children=self.sidebar.layout,
                            className=self.sidebar_div_class,
                            id="sticky-sidebar",
                        ),
                        html.Div(
                            children=self.content, className=self.content_div_class,
                        ),
                    ],
                    className="row py-3",
                ),
                className="container-fluid",
            ),
            id="body",
        )

    def update(self, fit: nonlinear_fit, meta: Optional[Dict] = None):
        """Updates sidebar and content from fit and meta configuration."""
        self.sidebar.update(fit.prior, meta)
        self._content = self.get_content(fit, meta)

    def get_content(
        self, fit: nonlinear_fit, meta: Optional[Dict] = None
    ) -> List[html.Base]:
        """Create default content block for fit object.

        This includes the plots for the data, residuals and details.
        """
        raise NotImplementedError()


class DefaultBodyTemplate(BodyTemplate):
    """The default body template of the app.

    This template adds a summary of the fit function as well as a panel for plots.
    Plots can be added by modifying the :attr:`DefaultBodyTemplate.plots` attribtute.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the template by adding default plots and callbacks."""
        super().__init__(*args, **kwargs)
        self.tex_function: bool = True
        """If true, try to render the fit function as latex."""
        self.plots: List[Dict[str, Any]] = DEFAULT_PLOTS
        """List of dictionaries specifying plots rendered in the tab element.
Must contain at least the `name: str` and `fcn:Callable[[nonlinear_fit], Figure]` items.

Example:
    Plot the fit results::

        def plot_fcn(fit):
            yy = fit.fcn(fit.x, fit.p)
            return plot_gvar(fit.x, yy, kind="band")

        gui = FitGUI(...)
        gui.body.plots.append({"name": "Fit results", "fcn": plot_fcn})

**Allowed keywords are**

* **name** *(str)*: The name presented in the tabs.
* **fcn** *(Callable[[nonlinear_fit], Figure])*: The function used to generate the plot. Must take a plot and kwargs as an input.
* **description** *(str)*: Text displayed below figure (can contain latex using).
* **kwargs** *(Dict[str, Any])*: A dictionary passed to the above function.
* **static_plot_gvar** *(Dict[str, Any])*: Static data passed to :func:`plot_gvar` added to the same figure (i.e., to also plot data as an comparison).

See also the :attr:`lsqfitgui.frontend.content.DEFAULT_PLOTS`.
"""  # noqa: E501
        self.additional_callbacks += [FCN_SOURCE_CALLBACK]
        """Callbacks present in the app. This adds the callback for toggeling the function source code.
        """

    def get_content(
        self, fit: nonlinear_fit, meta: Optional[Dict] = None
    ) -> List[html.Base]:
        """Adds content to the GUI."""
        figure_data = get_figures(fit, self.plots)
        content = [
            html.H1(children=self.name),
            html.Div(
                html.Div(
                    [
                        html.H4("Fit function"),
                        html.Div(
                            document_function(
                                fit.fcn,
                                fit.p,
                                x_dict_keys=list(fit.x.keys())
                                if isinstance(fit.x, dict)
                                else None,
                                tex_function=self.tex_function,
                            )
                        ),
                        html.H4("Fit parameters"),
                        html.Pre(str(fit)),
                    ],
                    className="col",
                ),
                className="row",
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        children=[dcc.Graph(figure=data["figure"])]
                        + (
                            [html.P(data["description"])]
                            if data.get("description")
                            else []
                        ),
                        label=data["label"],
                        value=data["tab-value"],
                    )
                    for data in figure_data
                ]
                + [
                    dcc.Tab(
                        children=[html.Pre(str(fit.format(maxline=True)))],
                        label="Details",
                        value="tab-details",
                    )
                ],
                value=figure_data[0]["tab-value"] if figure_data else "tab-details",
                persistence=True,
                persistence_type="local",
                persisted_props=["value"],
                id="content-tabs",
            ),
        ]
        return content
