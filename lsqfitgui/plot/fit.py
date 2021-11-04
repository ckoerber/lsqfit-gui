"""Plotting routines associated with fit objects."""
from typing import Optional

import gvar as gv
from plotly.graph_objects import Figure

from lsqfit import nonlinear_fit
from lsqfit._extras import chained_nonlinear_fit, unchained_nonlinear_fit

from lsqfitgui.plot.util import get_residuals
from lsqfitgui.plot.uncertainty import plot_gvar, interpolate


def plot_fit(fit, fig: Optional[Figure] = None):  # add type hint
    """Plot data and fit error bands."""
    try:
        xx = interpolate(fit.x)
        yy = fit.fcn(xx, fit.p)

        # Check that interpolated results make sense
        if isinstance(xx, dict) and isinstance(yy, (dict, gv.BufferDict)):
            for key, val in xx.items():
                assert len(val) == len(yy[key])
        elif isinstance(yy, (dict, gv.BufferDict)):
            for key, val in yy.items():
                assert len(val) == len(xx)
        else:
            assert len(xx) == len(yy)
    except Exception:

        if isinstance(fit, (chained_nonlinear_fit, unchained_nonlinear_fit)):
            xx = None
            yy = fit.fcn(fit.p)
        elif isinstance(fit, nonlinear_fit):
            xx = fit.x
            yy = fit.fcn(fit.x, fit.p)
        else:
            raise ValueError(f"Did not understand fit input of type {type(fit)}")

    fig = plot_gvar(
        xx, yy, kind="band", add_log_menu=True, scatter_kwargs={"name": "Fit"},
    )
    fig = plot_gvar(
        fit.x, fit.y, kind="errorbars", fig=fig, scatter_kwargs={"name": "Data"}
    )

    return fig


def plot_residuals(fit, fig: Optional[Figure] = None):
    """Plot fit residuals."""
    residuals = get_residuals(fit)
    fig = plot_gvar(
        fit.x, residuals, kind="errorbars", scatter_kwargs={"name": "Residuals"}
    )
    fig.add_hline(0, line={"color": "black"})

    return fig
