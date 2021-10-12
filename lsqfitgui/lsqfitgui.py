"""Lsqfit GUI."""
from typing import Optional, Callable, Dict, List, Any

#import functools
import os
from tempfile import NamedTemporaryFile

from gvar import dumps, evalcorr
from lsqfit import nonlinear_fit
from numpy import eye, allclose

from dash import Dash, html, dcc

from lsqfitgui.frontend.dashboard import (
    get_layout,
    update_layout_from_prior,
    update_layout_from_meta,
    toggle_prior_widget,
    EXTERNAL_STYLESHEETS,
    EXTERNAL_SCRIPTS,
    UPDATE_LAYOUT_CALLBACK_ARGS,
    SAVE_FIT_CALLBACK_ARGS,
    EXPORT_PRIOR_CALLBACK_ARGS,
    FCN_SOURCE_CALLBACK,
)


class FitGUI:
    """Class which initializes the dashboard."""

    plot_fcns = {}

    def __init__(
        self,
        fit: Optional[Dict] = None,
        name: Optional[str] = None,
        fit_setup_function: Optional[Callable] = None,
        fit_setup_kwargs: Optional[Dict] = None,
        meta_config: Optional[List[Dict]] = None,
        use_default_content: Optional[bool] = True,
        get_additional_content: Optional[html.Base] = None,
        plot_fcns: Optional[Dict[str, Callable]] = None,
        transformed_y: Optional[Dict] = None
    ):
        """Initialize the GUI."""
        self.name = name
        self._fit_setup_function = fit_setup_function
        self._fit_setup_kwargs = fit_setup_kwargs or {}
        self._meta_config = meta_config
        self.use_default_content = use_default_content
        self.get_additional_content = get_additional_content
        self.plot_fcns = plot_fcns or FitGUI.plot_fcns
        self.transformed_y = transformed_y or {}

        if fit is None and fit_setup_function is None:
            raise ValueError(
                "You must either specify the fit or fit setup function"
                " to initialize the GUI."
            )
        elif fit_setup_function is not None:
            self.initial_fit = fit_setup_function(**self._fit_setup_kwargs)
        else:
            self.initial_fit = fit

        if not allclose(
            evalcorr(self.initial_fit.prior.flatten()),
            eye(len(self.initial_fit.prior.flatten())),
        ):
            raise NotImplementedError("Prior of original fit contains correlations.")

        self._layout = get_layout(
            self.initial_fit,
            name=self.name,
            meta_config=self._meta_config,
            meta_values=self._fit_setup_kwargs,
            use_default_content=self.use_default_content,
            get_additional_content=self.get_additional_content,
            plot_fcns=self.plot_fcns,
            transformed_y=self.transformed_y
        )
        self._callbacks = [
            self._update_layout_callback,
            self._save_fit_callback,
            self._export_prior_callback,
            FCN_SOURCE_CALLBACK,
        ]

        self._setup_old = list(self._fit_setup_kwargs.values())
        self._prior_keys_old = None
        self._prior_values_old = None
        self._fit = self.initial_fit

    @property
    def fit(self):
        """Return current fit object."""
        return self._fit

    @property
    def layout(self):
        """Return the current layout."""
        return self._layout

    def setup(self, app):
        """Initialize the dash app."""
        app.title = self.name
        app.layout = html.Div(children=self.layout, id="body")
        for callback in self._callbacks:
            kwargs = callback.kwargs if hasattr(callback, "kwargs") else {}
            app.callback(*callback.args, **kwargs)(callback)

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
                use_default_content=self.use_default_content,
                get_additional_content=self.get_additional_content,
                plot_fcns=self.plot_fcns,
                transformed_y=self.transformed_y
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
                use_default_content=self.use_default_content,
                get_additional_content=self.get_additional_content,
                plot_fcns=self.plot_fcns,
                transformed_y=self.transformed_y
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
        """
        """
        return toggle_prior_widget(*args, **kwargs)

    _export_prior_callback.args = EXPORT_PRIOR_CALLBACK_ARGS
    _export_prior_callback.kwargs = {"prevent_initial_call": True}


def run_server(
    fit: Optional[nonlinear_fit] = None,
    name: str = "Lsqfit GUI",
    debug: bool = True,
    fit_setup_function: Optional[Callable[[Any], nonlinear_fit]] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
    use_default_content: Optional[bool] = True,
    get_additional_content: Optional[Callable[[nonlinear_fit], html.Base]] = None,
    run_app: bool = True,
    plot_fcns: Optional[Dict[str, Callable]] = None,
    transformed_y: Optional[Dict] = None,
    **kwargs,
) -> Dash:
    """Provide dashboard for lsqfitgui."""
    fit_gui = FitGUI(
        fit=fit,
        name=name,
        fit_setup_function=fit_setup_function,
        fit_setup_kwargs=fit_setup_kwargs,
        meta_config=meta_config,
        use_default_content=use_default_content,
        get_additional_content=get_additional_content,
        plot_fcns=plot_fcns,
        transformed_y=transformed_y
    )
    app = Dash(
        name,
        external_stylesheets=EXTERNAL_STYLESHEETS,
        external_scripts=EXTERNAL_SCRIPTS,
        assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
    )
    app.fit_gui = fit_gui
    fit_gui.setup(app)
    if run_app:
        app.run_server(debug=debug)
    return app

#from functools import wraps
'''
def plot(fcn):
    @functools.wraps(fcn)
    def wrapper(*args, **kwargs):
        return fcn(*args, **kwargs)

    FitGUI.plot_fcns[fcn.__name__] = fcn
 
    #setattr(FitGUI._plot_fcns, fcn.__name__, wrapper)
    return functools
'''