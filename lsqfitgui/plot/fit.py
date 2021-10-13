"""Plotting routines associated with fit objects."""
from typing import Optional

from plotly.graph_objects import Figure

from lsqfitgui.plot.util import get_residuals
from lsqfitgui.plot.uncertainty import plot_gvar


def plot_fit(fit, fig: Optional[Figure] = None):  # add type hint
    """Plot data and fit error bands."""
    fig = plot_gvar(
        fit.x, fit.fcn(fit.x, fit.p), name="Fit", kind="band", add_log_menu=True
    )
    fig = plot_gvar(fit.x, fit.y, name="Data", kind="data", fig=fig)

    return fig


def plot_residuals(fit, fig: Optional[Figure] = None):
    """Plot fit residuals."""
    residuals = get_residuals(fit)
    fig = plot_gvar(fit.x, residuals, name="Residuals", kind="data")
    fig.add_hline(0, line={"color": "black"})

    return fig
