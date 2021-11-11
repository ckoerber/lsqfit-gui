"""Provides dashboard for lsqfitgui."""
from typing import Optional, Dict, Any, Callable, List
from os import path

from dash import html, dcc
from dash.dependencies import Output

from dash_bootstrap_components.themes import BOOTSTRAP

from lsqfit import nonlinear_fit

from lsqfitgui.frontend.sidebar import Sidebar
from lsqfitgui.frontend.sidebar import EXPORT_PRIOR_CALLBACK  # noqa

from lsqfitgui.frontend.content import document_function, get_figures
from lsqfitgui.frontend.content import FCN_SOURCE_CALLBACK, DEFAULT_PLOTS  # noqa


class Body:
    def __init__(
        self,
        name: str = "Lsqfit GUI",
        meta_config: Optional[List[Dict[str, Any]]] = None,
    ):
        self.name = name
        self._sidebar = Sidebar(meta_config)
        self._content = html.Div()
        self._layout = html.Div()
        self.additional_callbacks = []

        self.update_callback_args = (
            Output("body", "children"),
            self.sidebar.update_callback_inputs,
        )

    @property
    def sidebar(self):
        return self._sidebar

    def update(self, fit: nonlinear_fit, meta: Optional[Dict] = None):
        self.sidebar.update(fit.prior, meta)
        self.sidebar.layout.className = "sticky-top bg-light p-4"
        self._content = self.get_content(fit)
        self._layout = html.Div(
            html.Div(
                children=html.Div(
                    children=[
                        html.Div(
                            children=self.sidebar.layout,
                            className="col-xs-12 col-sm-5 col-md-4 col-xl-3 col-xxl-2",
                            id="sticky-sidebar",
                        ),
                        html.Div(
                            children=self._content,
                            className="col-xs-12 col-sm-7 col-md-8 col-xl-9 col-xxl-10",
                        ),
                    ],
                    className="row py-3",
                ),
                className="container-fluid",
            ),
            id="body",
        )

    @property
    def layout(self):
        return self._layout

    def get_content(self, fit: nonlinear_fit):
        """Create default content block for fit object.

            This includes the plots for the data, residuals and details.
            """

        raise NotImplementedError()


class DefaultBody(Body):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tex_function: bool = True
        self.plots: List[Dict[str, Any]] = DEFAULT_PLOTS
        """List of dictionaries specifying plots rendered in the tab element.
                Must contain at least the `name: str` and `fcn:Callable[[nonlinear_fit], Figure]` items.

                Example:
                    Plot the fit results::

                        def plot_fcn(fit):
                            yy = fit.fcn(fit.x, fit.p)
                            return plot_gvar(fit.x, yy, kind="band")

                        gui.plots.append({"name": "Fit results", "fcn": plot_fcn})

                **Allowed keywords are**

                * **name** *(str)*: The name presented in the tabs.
                * **fcn** *(Callable[[nonlinear_fit], Figure])*: The function used to generate the plot. Must take a plot and kwargs as an input.
                * **description** *(str)*: Text displayed below figure (can contain latex using).
                * **kwargs** *(Dict[str, Any])*: A dictionary passed to the above function.
                * **static_plot_gvar** *(Dict[str, Any])*: Static data passed to :func:`plot_gvar` added to the same figure (i.e., to also plot data as an comparison).

                See also the :attr:`lsqfitgui.frontend.content.DEFAULT_PLOTS`.
                """  # noqa: E501
        self.additional_callbacks += [FCN_SOURCE_CALLBACK]

    def get_content(self, fit: nonlinear_fit):
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
