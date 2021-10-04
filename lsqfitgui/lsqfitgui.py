"""Lsqfit GUI."""
from typing import Optional, Callable, Dict, List, Any

from tempfile import NamedTemporaryFile

from gvar import dumps
from lsqfit import nonlinear_fit

from dash import Dash, html, dcc
from dash.dependencies import Input, Output

from lsqfitgui.frontend.dashboard import (
    get_layout,
    update_layout_from_prior,
    update_layout_from_meta,
    EXTERNAL_STYLESHEETS,
    DASHBOARD_PRIOR_INPUT,
    DASHBOARD_META_INPUT,
    SAVE_FIT_INPUT,
    SAVE_FIT_OUTPUT,
)


class FitGUI:
    """Class which initializes the dashboard."""

    def __init__(
        self,
        fit: Optional[Dict] = None,
        name: Optional[str] = None,
        fit_setup_function: Optional[Callable] = None,
        fit_setup_kwargs: Optional[Dict] = None,
        meta_config: Optional[List[Dict]] = None,
        use_default_content: Optional[bool] = True,
        get_additional_content: Optional[html.Base] = None,
    ):
        """Initialize the GUI."""
        self.name = name
        self._fit_setup_function = fit_setup_function
        self._fit_setup_kwargs = fit_setup_kwargs or {}
        self._meta_config = meta_config
        self.use_default_content = use_default_content
        self.get_additional_content = get_additional_content

        if fit is None and fit_setup_function is None:
            raise ValueError(
                "You must either specify the fit or fit setup function"
                " to initialize the GUI."
            )
        elif fit_setup_function is not None:
            self.initial_fit = fit_setup_function(**self._fit_setup_kwargs)
        else:
            self.initial_fit = fit

        self._layout = get_layout(
            self.initial_fit,
            meta_config=self._meta_config,
            meta_values=self._fit_setup_kwargs,
            use_default_content=self.use_default_content,
            get_additional_content=self.get_additional_content,
        )
        self._callbacks = [self._fit_callback, self._save_fit_callback]

        self._setup_old = list(self._fit_setup_kwargs.values())
        self._prior_old = None
        self._fit = self.initial_fit

    @property
    def fit(self):
        """Return current fit object."""
        return self._fit

    def update_layout(self, prior, setup):
        """Update the layout given new prior input."""
        if setup != self._setup_old:
            self._layout, self._fit = update_layout_from_meta(
                setup,
                self._fit_setup_function,
                self._fit_setup_kwargs,
                meta_config=self._meta_config,
                use_default_content=self.use_default_content,
                get_additional_content=self.get_additional_content,
            )
            self._setup_old = setup
        elif prior != self._prior_old:
            self._layout, self._fit = update_layout_from_prior(
                prior,
                self.fit,
                setup=setup,
                meta_config=self._meta_config,
                use_default_content=self.use_default_content,
                get_additional_content=self.get_additional_content,
            )
            self._prior_old = prior

    @property
    def layout(self):
        """Return the current layout."""
        return self._layout

    def _fit_callback(self, *args, **kwargs):
        self.update_layout(*args, **kwargs)
        return self.layout

    _fit_callback.output = Output("body", "children")
    _fit_callback.input = [
        Input(*DASHBOARD_PRIOR_INPUT),
        Input(*DASHBOARD_META_INPUT),
    ]

    def _save_fit_callback(self, *args, **kwargs):
        with NamedTemporaryFile() as out:
            out.write(dumps(self.fit))
            return dcc.send_file(out.name, filename="fit.p")

    _save_fit_callback.output = Output(*SAVE_FIT_OUTPUT)
    _save_fit_callback.input = [Input(*SAVE_FIT_INPUT)]
    _save_fit_callback.kwargs = {"prevent_initial_call": True}

    def setup(self, app):
        """Initialize the dash app."""
        app.title = self.name
        app.layout = html.Div(children=self.layout, id="body")
        for callback in self._callbacks:
            kwargs = callback.kwargs if hasattr(callback, "kwargs") else {}
            app.callback(callback.output, callback.input, **kwargs)(callback)


def run_server(
    fit: Optional[nonlinear_fit] = None,
    name: str = "Lsqfit GUI",
    debug: bool = True,
    fit_setup_function: Optional[Callable[[Any], nonlinear_fit]] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable[[nonlinear_fit], html.Base]] = None,
    **kwargs
):
    """Provide dashboard for lsqfitgui."""
    renderer = FitGUI(
        fit=fit,
        name=name,
        fit_setup_function=fit_setup_function,
        fit_setup_kwargs=fit_setup_kwargs,
        meta_config=meta_config,
        use_default_content=use_default_content,
        get_additional_content=get_additional_content,
    )
    app = Dash(name, external_stylesheets=EXTERNAL_STYLESHEETS)
    renderer.setup(app)
    app.run_server(debug=debug)
