"""This module provides interfaces for running a lsqfit dashboard GUI.

The :class:`FitGUI` class provides the interface to `lsqfit` providing dynamic html elements which can be embedded into a dash (flask) app.
The :func:`run_server` method provides a convinient interafce which also starts the Dash app which is accessible by any (local) browser.
"""  # noqa: E501
from typing import Optional, Callable, Dict, List, Any

from tempfile import NamedTemporaryFile

from numpy import eye, allclose
from gvar import dumps, evalcorr
from lsqfit import nonlinear_fit
from lsqfit._extras import unchained_nonlinear_fit

from dash import Dash, html, dcc

from lsqfitgui.frontend.dashboard import (
    get_layout,
    update_layout_from_prior,
    update_layout_from_meta,
    toggle_prior_widget,
    EXTERNAL_STYLESHEETS,
    EXTERNAL_SCRIPTS,
    ASSETS,
    UPDATE_LAYOUT_CALLBACK_ARGS,
    SAVE_FIT_CALLBACK_ARGS,
    EXPORT_PRIOR_CALLBACK_ARGS,
    FCN_SOURCE_CALLBACK,
    DEFAULT_PLOTS,
)
from lsqfitgui.util.models import (
    lsqfit_from_multi_model_fit,
    lsqfit_from_multi_model_fit_wrapper,
)


class FitGUI:
    """Class which initializes the dashboard."""

    def __init__(  # ignore: D107
        self,
        fit: Optional[nonlinear_fit] = None,
        fit_setup_function: Optional[Callable] = None,
        fit_setup_kwargs: Optional[Dict] = None,
        meta_config: Optional[List[Dict]] = None,
        use_default_content: bool = True,
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
        self.name: str = None
        """Name of the app displayed as title and browser tab title."""
        self._fit_setup_function = fit_setup_function
        self._fit_setup_kwargs = fit_setup_kwargs or {}
        self._meta_config = meta_config
        self._use_default_content = use_default_content
        self._layout = None

        self.get_additional_content: Callable[[nonlinear_fit], html.Base] = None
        """Function used to determine dynamic content depending on fit results."""

        self.plots: List[Dict[str, Any]] = []
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

        if self._use_default_content:
            self.plots += DEFAULT_PLOTS

        if fit is None and fit_setup_function is None:
            raise ValueError(
                "You must either specify the fit or fit setup function"
                " to initialize the GUI."
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
            evalcorr(self.initial_fit.prior.flatten()),
            eye(len(self.initial_fit.prior.flatten())),
        ):
            raise NotImplementedError("Prior of original fit contains correlations.")

        self._callbacks = [
            self._update_layout_callback,
            self._save_fit_callback,
            self._export_prior_callback,
        ]
        if self._use_default_content:
            self._callbacks += [FCN_SOURCE_CALLBACK]

        self._setup_old = list(self._fit_setup_kwargs.values())
        self._prior_keys_old = None
        self._prior_values_old = None
        self._fit = self.initial_fit
        self._app = None

    @property
    def fit(self) -> nonlinear_fit:
        """Return current fit object."""
        return self._fit

    @property
    def initial_fit(self) -> nonlinear_fit:
        """Return fit object used to initialize the app."""
        return self._initial_fit

    @property
    def layout(self) -> html.Base:
        """Return the current layout."""
        if self._layout is None:
            self._layout = get_layout(
                self.initial_fit,
                name=self.name,
                meta_config=self._meta_config,
                meta_values=self._fit_setup_kwargs,
                use_default_content=self._use_default_content,
                get_additional_content=self.get_additional_content,
                plots=self.plots,
            )
        return self._layout

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

        if not app:
            app = Dash(
                self.name,
                external_stylesheets=EXTERNAL_STYLESHEETS,
                external_scripts=EXTERNAL_SCRIPTS,
                assets_folder=ASSETS,
            )

        app.title = self.name
        app.layout = html.Div(children=self.layout, id="body")
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

    def _update_layout_callback(self, prior_ids, prior_values, setup):
        """Update the layout given new prior input."""
        prior_keys = [idx["name"] for idx in prior_ids]
        if setup != self._setup_old:
            self._layout, self._fit = update_layout_from_meta(
                setup,
                self._fit_setup_function,
                self._fit_setup_kwargs,
                name=self.name,
                meta_config=self._meta_config,
                use_default_content=self._use_default_content,
                get_additional_content=self.get_additional_content,
                plots=self.plots,
            )
            self._setup_old = setup
        elif (
            prior_keys != self._prior_keys_old or prior_values != self._prior_values_old
        ):
            self._layout, self._fit = update_layout_from_prior(
                dict(zip(prior_keys, prior_values)),
                self.fit,
                setup=setup,
                name=self.name,
                meta_config=self._meta_config,
                use_default_content=self._use_default_content,
                get_additional_content=self.get_additional_content,
                plots=self.plots,
            )
            self._prior_keys_old = prior_keys
            self._prior_values_old = prior_values
        return self.layout

    _update_layout_callback.args = UPDATE_LAYOUT_CALLBACK_ARGS
    _update_layout_callback.kwargs = {"prevent_initial_call": True}

    def _save_fit_callback(self, *args, **kwargs):
        with NamedTemporaryFile() as out:
            out.write(dumps(self.fit))
            return dcc.send_file(out.name, filename="fit.p")

    _save_fit_callback.args = SAVE_FIT_CALLBACK_ARGS
    _save_fit_callback.kwargs = {"prevent_initial_call": True}

    def _export_prior_callback(self, *args, **kwargs):
        return toggle_prior_widget(*args, **kwargs)

    _export_prior_callback.args = EXPORT_PRIOR_CALLBACK_ARGS
    _export_prior_callback.kwargs = {"prevent_initial_call": True}


def run_server(
    fit: Optional[nonlinear_fit] = None,
    name: str = "Lsqfit GUI",
    fit_setup_function: Optional[Callable[[Any], nonlinear_fit]] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable[[nonlinear_fit], html.Base]] = None,
    additional_plots: Optional[Dict[str, Callable]] = None,
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
        use_default_content=use_default_content,
    )
    fit_gui.name = name
    fit_gui.get_additional_content = get_additional_content
    fit_gui.plots += additional_plots or []
    fit_gui.setup_app()
    if run_app:
        import webbrowser
        from threading import Timer

        Timer(1, lambda: webbrowser.open_new(f"http://{host}:{port}")).start()
        fit_gui.run_server(host=host, debug=debug, port=port)

    return fit_gui
