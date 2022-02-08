"""Utility functions for converting fit models."""
from lsqfit import nonlinear_fit


def fit_with_xy(fit: nonlinear_fit,) -> nonlinear_fit:
    """Convert a fit with only y-data argument to a fit with data=(x,y)."""  # noqa: D202

    def fcn(x, p):
        return fit.fcn(p)

    fcn._lsqfitgui_fcn_src = (
        fit.fcn._lsqfitgui_fcn_src
        if hasattr(fit.fcn, "_lsqfitgui_fcn_src")
        else fit.fcn
    )

    return nonlinear_fit(([], fit.data), fcn=fcn, prior=fit.prior)


def fit_with_xy_wrapper(fcn):
    """Wrap a generate fit function to return a fit_with_xy."""

    def wrapped_fit_with_xy(**kwargs):
        return fit_with_xy(fcn(**kwargs))

    return wrapped_fit_with_xy
