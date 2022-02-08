"""Utility functions for converting fit models."""
from lsqfit import nonlinear_fit


def fit_with_prior_dict(fit: nonlinear_fit,) -> nonlinear_fit:
    """Convert a fit with prior array to a fit with a prior dict."""  # noqa: D202

    def fcn(x, p):
        return fit.fcn(x, p["p"])

    fcn._lsqfitgui_fcn_src = (
        fit.fcn._lsqfitgui_fcn_src
        if hasattr(fit.fcn, "_lsqfitgui_fcn_src")
        else fit.fcn
    )

    return nonlinear_fit(fit.data, fcn=fcn, prior={"p": fit.prior})


def fit_with_prior_dict_wrapper(fcn):
    """Wrap a generate fit function to return a fit_with_prior_dict."""

    def wrapped_fit_with_prior_dict(**kwargs):
        return fit_with_prior_dict(fcn(**kwargs))

    return wrapped_fit_with_prior_dict
