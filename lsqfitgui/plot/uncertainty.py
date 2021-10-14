"""Plotting shortcuts for plotly error plots and bands."""
from typing import Optional, Dict, Any

import numpy as np
import gvar as gv

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lsqfitgui.plot.util import LOG_MENU


def wrap_plot_gvar(
    kind: str = "band",
    add_log_menu: bool = False,
    scatter_kwargs: Optional[Dict] = None,
):
    """Wrapper to generate plot of gvars for functions."""

    def wrapper(fcn):
        def get_figure_from_fcn(fit, **fcn_kwargs):
            xx = fit.x
            if kind == "band":
                try:
                    x_min, x_max = np.nanmin(fit.x), np.nanmax(fit.x)
                    xx = np.linspace(x_min, x_max)
                except Exception:
                    pass

            return plot_gvar(
                xx,
                fcn(xx, fit.p, **fcn_kwargs),
                fig=None,
                kind=kind,
                add_log_menu=add_log_menu,
                scatter_kwargs=scatter_kwargs,
            )

        return get_figure_from_fcn

    return wrapper


def plot_gvar(
    x,
    y,
    fig: Optional[go.Figure] = None,
    kind: str = "band",
    add_log_menu: bool = False,
    scatter_kwargs: Optional[Dict] = None,
):
    """Plots gvars."""
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
            sub_scatter_kwargs["name"] = sub_scatter_kwargs.get("name", "") + ", {key}"
            if kind == "errorbars":
                plot_errorbars(
                    fig,
                    x[key] if isinstance(x, dict) else x,
                    mean,
                    sdev,
                    scatter_kwargs=sub_scatter_kwargs,
                    trace_kwargs={"row": n + 1, "col": 1},
                )
            elif kind == "band":
                plot_band(
                    fig,
                    x[key] if isinstance(x, dict) else x,
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
