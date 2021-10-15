"""Plotting shortcuts for plotly errorbar plots and bands."""
from typing import Optional, Dict, Any, Union, Callable

import numpy as np
import gvar as gv

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lsqfit import nonlinear_fit
from lsqfitgui.plot.util import LOG_MENU


def interpolate(x, n=100):
    """Tries to interpolate nested dictionaries of arrays."""
    try:
        if isinstance(x, dict):
            xx = {}
            for key, val in x.items():
                xx[key] = interpolate(val, n=n)
        else:
            xmin, xmax = np.nanmin(x), np.nanmax(x)
            xx = np.linspace(xmin, xmax, num=n)
    except Exception:
        xx = x
    return xx


def wrap_plot_gvar(
    kind: str = "band",
    add_log_menu: bool = False,
    scatter_kwargs: Optional[Dict] = None,
) -> Callable[[nonlinear_fit], go.Figure]:
    """Wraps functions taking `x` and `p` arguments such that they can be used by the :attr:`lsqfitgui.FitGUI.plots` to generate plots of gvars.

    Arguments:
        kind: Allowed values: "band", "errorbar".
            Returned figure will contain errorbars or errorbands.
        add_log_menu: Should the returned figure have an menu allowing to change from regular to log y-axis?
        scatter_kwargs: Keyword arguments passed to go.Scatter().

    Example:
        The code below presents how to use the wrapper to add new plots to the gui::

            def fcn(x, p):
                yy = ...
                return yy

            def plot_fcn(fit):
                yy = fcn(fit.x, fit.p)
                return plot_gvar(fit.x, yy, kind="band")

            @wrap_plot_gvar(kind="bands")
            def wrapped_fcn(x, p):
                return fcn(x, p)

            gui.plots.append({"name": "Fcn results", "fcn": wrapped_fcn})

        Both functions, `wrapped_fcn` and `plot_fcn` will produce the same plot when added to the gui.
    """  # noqa: E501, D202, D401

    def wrapper(fcn):
        def get_figure_from_fcn(fit, **fcn_kwargs):
            if kind == "band":
                try:
                    xx = interpolate(fit.x)
                    yy = fcn(xx, fit.p)
                except Exception:
                    xx = fit.x
                    yy = fcn(fit.x, fit.p)

            return plot_gvar(
                xx,
                yy,
                fig=None,
                kind=kind,
                add_log_menu=add_log_menu,
                scatter_kwargs=scatter_kwargs,
            )

        return get_figure_from_fcn

    return wrapper


def plot_gvar(
    x: Union[np.ndarray, Dict[str, np.ndarray]],
    y: gv.BufferDict,
    fig: Optional[go.Figure] = None,
    kind: str = "band",
    add_log_menu: bool = False,
    scatter_kwargs: Optional[Dict] = None,
) -> go.Figure:
    """Plot gvars as go.Figures including their uncertainties.

    Arguments:
        x: The independent variable.
            Can be either an array or a dictionary of arrays where keys must match the keys of the dependent variable.
            If `kind="band"`, tries to interpolate the values.
        y: The dependent variable.
            If it is a dictionary of gvar arrays, the figure will contain several sub figures.
        fig: Figure to add traces to. If not specified, creates a new figure.
        kind: Either "band" or "errorbars".
        add_log_menu: Add a menu to switch from a linear to a log scale.
            Only available if `y` is not a dictionary.
        scatter_kwargs: Keyword arguments passed to `go.Scatter`.
    """  # noqa: E501
    fig_was_none = fig is None
    scatter_kwargs = scatter_kwargs or {}

    if not isinstance(y, (dict, gv.BufferDict)):
        fig = fig or go.Figure()
        mean = gv.mean(y)
        sdev = gv.sdev(y)

        if kind == "errorbars":
            plot_errorbars(fig, x, mean, sdev, scatter_kwargs=scatter_kwargs)
        elif kind == "band":
            plot_band(
                fig, x, mean - sdev, mean, mean + sdev, scatter_kwargs=scatter_kwargs
            )
        else:
            raise KeyError(f"Does not know how to plot {kind}")
    else:
        fig = fig or make_subplots(cols=1, rows=len(y), subplot_titles=list(y.keys()))

        for n, (key, yy) in enumerate(y.items()):
            mean = gv.mean(y[key])
            sdev = gv.sdev(y[key])
            sub_scatter_kwargs = scatter_kwargs.copy()
            sub_scatter_kwargs["name"] = sub_scatter_kwargs.get("name", "") + f", {key}"

            xx = x[key] if isinstance(x, dict) else x
            if kind == "errorbars":
                plot_errorbars(
                    fig,
                    xx,
                    mean,
                    sdev,
                    scatter_kwargs=sub_scatter_kwargs,
                    trace_kwargs={"row": n + 1, "col": 1},
                )
            elif kind == "band":
                plot_band(
                    fig,
                    xx,
                    mean - sdev,
                    mean,
                    mean + sdev,
                    scatter_kwargs=sub_scatter_kwargs,
                    trace_kwargs={"row": n + 1, "col": 1},
                )

        if fig_was_none:
            fig.update_layout(height=len(y) * 300)

    if fig_was_none:
        fig.update_layout(
            template="plotly_white",
            font={"size": 16},
            hoverlabel={"font_size": 16},
            updatemenus=None
            if isinstance(y, (dict, gv.BufferDict)) or not add_log_menu
            else [LOG_MENU],
        )

    return fig


def plot_errorbars(
    fig,
    x,
    y,
    err,
    scatter_kwargs: Optional[Dict[str, Any]] = None,
    trace_kwargs: Optional[Dict[str, Any]] = None,
):
    """Scatter plot with data errors."""
    x = np.arange(len(y)) if not isinstance(x, (list, np.ndarray)) else x
    scatter_kwargs = scatter_kwargs or {}
    trace_kwargs = trace_kwargs or {}
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            error_y={"type": "data", "array": err},
            mode="markers",
            **scatter_kwargs,
        ),
        **trace_kwargs,
    )


def plot_band(
    fig,
    x,
    y_min,
    y_mean,
    y_max,
    scatter_kwargs: Optional[Dict[str, Any]] = None,
    trace_kwargs: Optional[Dict[str, Any]] = None,
):
    """Error band plot."""
    if not isinstance(x, (list, np.ndarray)):
        x = np.arange(len(y_mean))

    trace_kwargs = trace_kwargs or {}

    scatter_kwargs = scatter_kwargs.copy() or {}
    scatter_kwargs["opacity"] = scatter_kwargs.get("opacity", 0.8)
    scatter_kwargs["line_color"] = scatter_kwargs.get("line_color", "indigo")
    scatter_kwargs["legendgroup"] = scatter_kwargs.get(
        "legendgroup", scatter_kwargs.get("name")
    )

    fig.add_trace(
        go.Scatter(
            x=list(x) + list(x)[::-1],
            y=list(y_max) + list(y_min)[::-1],
            fill="toself",
            mode="lines",
            **scatter_kwargs,
        ),
        **trace_kwargs,
    )
    scatter_kwargs["showlegend"] = False
    fig.add_trace(
        go.Scatter(x=x, y=y_mean, mode="lines", **scatter_kwargs,), **trace_kwargs,
    )
