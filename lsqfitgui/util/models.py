"""Utility functions for converting fit models."""
from lsqfit._extras import unchained_nonlinear_fit
from lsqfit import nonlinear_fit


def lsqfit_from_multi_model_fit(
    multi_model_fit: unchained_nonlinear_fit,
) -> nonlinear_fit:
    """Convert a unchained nonlinear fit object created by ``lsqfit.MultiFitter.lsqfit`` to a nonlinear_fit object."""  # noqa: E501
    fitter, kwargs, fkwargs = multi_model_fit.fitter_args_kargs

    assert fitter.__name__ == "lsqfit"

    models = kwargs["models"]
    data = kwargs["data"]
    prior = kwargs["prior"]

    x_data = {m.datatag: getattr(m, "x", None) for m in models}
    y_data = {m.datatag: m.builddata(data) for m in models}

    def fcn(x, p):
        return {m.datatag: m.fitfcn(m.buildprior(p)) for m in models}

    fit = nonlinear_fit((x_data, y_data), fcn=fcn, prior=prior)
    fit.models = models

    return fit


def lsqfit_from_multi_model_fit_wrapper(fcn):
    """Wrap a generate fit function to return a lsqfit_from_multi_model_fit."""

    def wrapped_lsqfit_from_multi_model_fit(**kwargs):
        return lsqfit_from_multi_model_fit(fcn(**kwargs))

    return wrapped_lsqfit_from_multi_model_fit
