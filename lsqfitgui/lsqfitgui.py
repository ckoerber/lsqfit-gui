"""This module provides interfaces for running a lsqfit dashboard GUI.

The :class:`FitGUI` class provides the interface to `lsqfit` providing dynamic html elements which can be embedded into a dash (flask) app.
The :func:`run_server` method provides a convinient interafce which also starts the Dash app which is accessible by any (local) browser.
"""  # noqa: E501
from typing import Optional, Callable, Dict, List, Any, Type

from tempfile import NamedTemporaryFile

from numpy import eye, allclose
from gvar import dumps, evalcorr
from lsqfit import nonlinear_fit
from lsqfit._extras import unchained_nonlinear_fit

from dash import Dash, html, dcc

from lsqfitgui.frontend.body import (
    BodyTemplate,
    DefaultBodyTemplate,
    EXTERNAL_STYLESHEETS,
    EXTERNAL_SCRIPTS,
    ASSETS,
)
from lsqfitgui.backend import process_meta, process_priors
from lsqfitgui.util.models import (
    lsqfit_from_multi_model_fit,
    lsqfit_from_multi_model_fit_wrapper,
)
from lsqfitgui.util.callback import CallbackWrapper


class FitGUI:
    """Class which initializes the dashboard."""

    def __init__(  # ignore: D107
        self,
        fit: Optional[nonlinear_fit] = None,
        fit_setup_function: Optional[Callable] = None,
        fit_setup_kwargs: Optional[Dict] = None,
        meta_config: Optional[List[Dict]] = None,
        template_cls: Type[BodyTemplate] = DefaultBodyTemplate,
    ):
        """Initialize the fit gui.

        You must either provide a `fit` object or a `fit_setup_function` function to initialize this class.
        Note that this dose not create a ``Dash`` app; the app is created by calling :meth:`FitGUI.setup_app` (which is implicitly called by :meth:`FitGUI.run_server`).

        Arguments:
            fit: Non-linear fit object.
            fit_setup_function: Function which returns a non-linear fit object.
                Its keywords are provided by `fit_setup_kwargs`.
            fit_setup_kwargs: Initial kwargs which are passed to the `fit_setup_function` for creating the first fit object.
            meta_config: Configuration for the fit_setup_kwargs represented in the GUI.
                These must match `dcc.Input <https://dash.plotly.com/dash-core-components/input#input-properties>`_ arguments.
            use_default_content: Add default elements like the function documentation and plot tabs to the GUI.
            template_cls: Class which renders the html body. Must inherit from  :class:`lsqfitgui.frontend.body.BodyTemplate`.

        Example:
            The most basic example just requires a nonlinear_fit object::

                fit = lsqfit.nonlinear_fit(data, fcn=fcn, prior=prior)
                gui = FitGUI(fit)

            More sophisticated examples, where also meta arguments are used, are::

                from dash import Dash

                def generate_fit(n_exp=3):
                    ...
                    return lsqfit.nonlinear_fit(data, fcn=fcn, prior=prior)

                fit_setup_kwargs = {"n_exp": 3}
                meta_config = [{"name": "n_exp", "type": "number", "min": 1, "max": 10, "step": 1}]

                gui = FitGUI(
                    fit_setup_function=generate_fit,
                    fit_setup_kwargs=fit_setup_kwargs,
                    meta_config=meta_config
                )
                fit_gui.run_server(host=host, debug=debug, port=port)
        """  # noqa: E501
        self._name: str = "Lsqfit GUI"
        """Name of the app displayed as title and browser tab title."""
        self._fit_setup_function = fit_setup_function
        self._fit_setup_kwargs = fit_setup_kwargs or {}
        self._meta_config = meta_config
        self._body = template_cls(self.name, self._meta_config)

        if fit is None and fit_setup_function is None:
            raise ValueError(
                "You must either specify the fit or fit setup function" " to initialize the GUI."
            )
        elif fit_setup_function is not None:
            self._initial_fit = fit_setup_function(**self._fit_setup_kwargs)
        else:
            self._initial_fit = fit

        if isinstance(self._initial_fit, unchained_nonlinear_fit):
            self._initial_fit = lsqfit_from_multi_model_fit(self._initial_fit)
            if self._fit_setup_function is not None:
                self._fit_setup_function = lsqfit_from_multi_model_fit_wrapper(
                    self._fit_setup_function
                )

        if not allclose(
            evalcorr(self.initial_fit.prior.flatten()), eye(len(self.initial_fit.prior.flatten())),
        ):
            raise NotImplementedError("Prior of original fit contains correlations.")

        self._callbacks: List[CallbackWrapper] = [
            CallbackWrapper(self._update_layout_callback, self.body.update_callback_args),
            CallbackWrapper(self._save_fit_callback, self.body.sidebar.save_fit_callback_args),
            self.body.sidebar.export_prior_callback,
        ] + self.body.additional_callbacks

        self._meta_values_old = list(self._fit_setup_kwargs.values())
        self._prior_keys_old = None
        self._prior_values_old = None
        self._fit = self.initial_fit
        self._app = None

    @property
    def fit(self) -> nonlinear_fit:
        """Return current fit object."""
        return self._fit

    @property
    def body(self) -> BodyTemplate:
        """Returns the html body instance."""
        return self._body

    @property
    def name(self) -> str:
        """Return name of the app."""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self.body.name = value

    @property
    def initial_fit(self) -> nonlinear_fit:
        """Return fit object used to initialize the app."""
        return self._initial_fit

    @property
    def layout(self) -> html.Base:
        """Return the current layout."""
        return self.body.layout

    def setup_app(self, app: Optional[Dash] = None):
        """Initialize the dash app.

        Sets up layout and callbacks and create a ``Dash`` instance if not provided.

        Arguments:
            app: The dash app which runs the server.
                If provided, requires to manually set up style sheets, scripts and assets.

        Raises RuntimeError if app already set up.
        """
        if self._app is not None:
            raise RuntimeError("App already initialized.")

        # load body for the first time
        self.body.update(self.initial_fit, self._fit_setup_kwargs)

        if not app:
            app = Dash(
                self.name,
                external_stylesheets=EXTERNAL_STYLESHEETS,
                external_scripts=EXTERNAL_SCRIPTS,
                assets_folder=ASSETS,
            )

        app.title = self.name
        app.layout = self.layout
        for callback in self._callbacks:
            kwargs = callback.kwargs if hasattr(callback, "kwargs") else {}
            app.callback(*callback.args, **kwargs)(callback)

        self._app = app

    @property
    def app(self) -> Dash:
        """Return plotly dash app."""
        return self._app

    def run_server(self, *args, **kwargs):
        """Wrapper to self.app.run_server."""
        if not self.app:
            self.setup_app()
        return self.app.run_server(*args, **kwargs)

    # Callbacks

    def _update_layout_from_prior(
        self, prior_keys, prior_values, meta_values: Optional[List[str]] = None
    ):
        """Parse prior form input values to create new layout.

        Creates new fit object for new prior and calls get_layout.
        """
        meta = process_meta(meta_values, self._meta_config)
        prior = dict(zip(prior_keys, prior_values))
        self._fit = process_priors(prior, self.fit)
        self.body.update(self.fit, meta)

    def _update_layout_from_meta(self, meta_values):
        """Parse meta form input values to create new layout.

        Creates new fit object for new meta data and prior (using fit_setup_function)
        and calls get_layout.
        """
        meta = process_meta(meta_values, self._meta_config)
        meta = {key: meta.get(key) or val for key, val in self._fit_setup_kwargs.items()}
        self._fit = self._fit_setup_function(**meta)
        self.body.update(self.fit, meta)

    def _update_layout_callback(self, prior_ids, prior_values, meta_values):
        """Update the layout given new prior input."""
        prior_keys = [idx["name"] for idx in prior_ids]
        if meta_values != self._meta_values_old:
            self._meta_values_old = meta_values
            self._update_layout_from_meta(meta_values)
        elif prior_keys != self._prior_keys_old or prior_values != self._prior_values_old:
            self._prior_keys_old = prior_keys
            self._prior_values_old = prior_values
            self._update_layout_from_prior(prior_keys, prior_values, meta_values=meta_values)
        return self.layout.children

    def _save_fit_callback(self, *args, **kwargs):
        with NamedTemporaryFile() as out:
            out.write(dumps(self.fit))
            return dcc.send_file(out.name, filename="fit.p")


def run_server(
    fit: Optional[nonlinear_fit] = None,
    name: str = "Lsqfit GUI",
    fit_setup_function: Optional[Callable[[Any], nonlinear_fit]] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
    additional_plots: Optional[List[Dict[str, Callable]]] = None,
    tex_function: bool = True,
    run_app: bool = True,
    debug: bool = True,
    host: str = "localhost",
    port: int = 8000,
) -> FitGUI:
    """Initialize the GUI and start the dash app.

    Requires either a `fit` object or a `fit_setup_function`.

    Arguments:
        fit: Non-linear fit object.
        name: Name of the app displayed as title and browser tab title.
        fit_setup_function: Function which returns a non-linear fit object.
            Its keywords are provided by `fit_setup_kwargs`.
        fit_setup_kwargs: Initial kwargs which are passed to the `fit_setup_function` for creating the first fit object.
        meta_config: Configuration for the fit_setup_kwargs represented in the GUI.
            These must match `dcc.Input <https://dash.plotly.com/dash-core-components/input#input-properties>`_ arguments.
        use_default_content: Add default elements like the function documentation and plot tabs to the GUI.
        get_additional_content: Function used to determine dynamic content depending on fit results.
        tex_function: Try to render the fit function as latex.
        additional_plots: List of dictionaries specifying plots rendered in the tab element.
            Must contain at least the `name: str` and `fcn:Callable[[nonlinear_fit], Figure]` items.
            This populates :attr:`FitGUI.plots`.
            See also the :attr:`lsqfitgui.frontend.content.DEFAULT_PLOTS`.
        run_app: Call run server on the dash app.
        debug: Run the dash app in debug mode. Only used if `run_app=True`.
        host: The hosting address of the dash app. Only used if `run_app=True`.
        port: The port of the dash app. Only used if `run_app=True`.

    Example:
        The most basic example just requires a nonlinear_fit object::

            fit = lsqfit.nonlinear_fit(data, fcn=fcn, prior=prior)
            app = run_server(fit)

        More sophisticated examples, where also meta arguments are used, are::

            def generate_fit(n_exp=3):
                ...
                return lsqfit.nonlinear_fit(data, fcn=fcn, prior=prior)

            fit_setup_kwargs = {"n_exp": 3}
            meta_config = [{"name": "n_exp", "type": "number", "min": 1, "max": 10, "step": 1}]

            fit_gui = run_server(
                fit_setup_function=generate_fit,
                fit_setup_kwargs=fit_setup_kwargs,
                meta_config=meta_config
            )
    """  # noqa: E501
    fit_gui = FitGUI(
        fit=fit,
        fit_setup_function=fit_setup_function,
        fit_setup_kwargs=fit_setup_kwargs,
        meta_config=meta_config,
        template_cls=DefaultBodyTemplate,
    )
    fit_gui.name = name
    assert isinstance(fit_gui.body, DefaultBodyTemplate)
    fit_gui.body.tex_function = tex_function
    fit_gui.body.plots += additional_plots or []
    fit_gui.setup_app()
    if run_app:
        fit_gui.run_server(host=host, debug=debug, port=port)
    return fit_gui
