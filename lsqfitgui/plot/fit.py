"""Plotting routines associated with fit objects."""
from typing import Optional

from plotly.graph_objects import Figure

from lsqfitgui.plot.util import get_residuals
from lsqfitgui.plot.uncertainty import plot_gvar


def plot_fit(fit, fig: Optional[Figure] = None):  # add type hint
    """Plot data and fit error bands."""
    fig = plot_gvar(
        fit.x,
        fit.fcn(fit.x, fit.p),
        kind="band",
        add_log_menu=True,
        scatter_kwargs={"name": "Fit"},
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
