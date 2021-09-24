"""Lsqfit GUI."""
from typing import Optional, Callable, Dict, List

from dash import Dash, html
from dash.dependencies import Input, Output

from lsqfitgui.frontend.dashboard import (
    get_layout,
    update_layout,
    EXTERNAL_STYLESHEETS,
    DASHBOARD_PRIOR_INPUT,
)


class FitGUI:
    """Class which initializes the dashboar."""

    def __init__(
        self,
        fit: Optional[Dict] = None,
        name: Optional[str] = None,
        fit_setup_function: Optional[Callable] = None,
        fit_setup_kwargs: Optional[Dict] = None,
        meta_config: Optional[List[Dict]] = None,
    ):
        """Initialize the GUI."""
        self.name = name
        self._fit_setup_function = fit_setup_function
        self._fit_setup_kwargs = fit_setup_kwargs or {}
        self._meta_config = meta_config

        if fit is None and fit_setup_function is None:
            raise ValueError(
                "You must either specify the fit or fit setup function"
                " to initialize the GUI."
            )
        elif fit_setup_function is not None:
            self.initial_fit = fit_setup_function(**self._fit_setup_kwargs)
        else:
            self.initial_fit = fit

        self._layout = get_layout(self.initial_fit, meta_config=self._meta_config)
        self._callbacks = [self._prior_callback]

    def update_layout(self, prior):
        """Update the layout given new prior input."""
        self._layout = update_layout(
            prior, self.initial_fit, meta_config=self._meta_config
        )

    @property
    def layout(self):
        """Return the current layout."""
        return self._layout

    def _prior_callback(self, *args, **kwargs):
        self.update_layout(*args, **kwargs)
        return self.layout

    _prior_callback.output = Output("body", "children")
    _prior_callback.input = Input(*DASHBOARD_PRIOR_INPUT)

    def setup(self, app):
        """Initialize the dash app."""
        app.title = self.name
        app.layout = html.Div(children=self.layout, id="body")
        for callback in self._callbacks:
            app.callback(callback.output, callback.input)(callback)


def run_server(
    fit: Optional[Dict] = None,
    name: str = "Lsqfit GUI",
    debug: bool = True,
    fit_setup_function: Optional[Callable] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
    **kwargs
):
    """Provide dashboard for lsqfitgui."""
    renderer = FitGUI(
        fit=fit,
        name=name,
        fit_setup_function=fit_setup_function,
        fit_setup_kwargs=fit_setup_kwargs,
        meta_config=meta_config,
    )
    app = Dash(name, external_stylesheets=EXTERNAL_STYLESHEETS)
    renderer.setup(app)
    app.run_server(debug=debug)
