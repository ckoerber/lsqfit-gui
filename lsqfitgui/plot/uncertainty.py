"""Plotting shortcuts for plotly error plots and bands."""
from typing import Optional, Dict, Any

import numpy as np
import gvar as gv

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lsqfitgui.plot.util import LOG_MENU


def wrap_plot_function(kind: str = "data", **wrapper_kwargs):
    """Wrapper to generate plot of gvars for functions."""

    def wrapper(fcn):
        def get_figure_from_fcn(fit, **fcn_kwargs):
            return plot_gvar(
                fit.x,
                fcn(fit.x, fit.p, **fcn_kwargs),
                fig=None,
                kind=kind,
                **wrapper_kwargs,
            )

        return get_figure_from_fcn

    return wrapper


def plot_gvar(
    x,
    y,
    fig: Optional[go.Figure] = None,
    kind: str = "data",
    name: Optional[str] = None,
    add_log_menu: bool = False,
    **kwargs,
):
    """Plots gvars."""
    fig_was_none = fig is None

    if not isinstance(y, (dict, gv.BufferDict)):
        fig = fig or go.Figure()
        mean = gv.mean(y)
        sdev = gv.sdev(y)

        if kind == "data":
            plot_errors(fig, x, mean, sdev, name=name, scatter_kwargs=kwargs)
        elif kind == "band":
            plot_band(
                fig, x, mean - sdev, mean, mean + sdev, name=name, scatter_kwargs=kwargs
            )
        else:
            raise KeyError(f"Does not know how to plot {kind}")
    else:
        fig = fig or make_subplots(cols=1, rows=len(y), subplot_titles=list(y.keys()))

        for n, (key, yy) in enumerate(y.items()):
            mean = gv.mean(y[key])
            sdev = gv.sdev(y[key])
            if kind == "data":
                plot_errors(
                    fig,
                    x[key] if isinstance(x, dict) else x,
                    mean,
                    sdev,
                    name=f"{name} {key} data",
                    row=n + 1,
                    scatter_kwargs=kwargs,
                    col=1,
                )
            elif kind == "band":
                plot_band(
                    fig,
                    x[key] if isinstance(x, dict) else x,
                    mean - sdev,
                    mean,
                    mean + sdev,
                    name=f"{name} {key} fit",
                    scatter_kwargs=kwargs,
                    row=n + 1,
                    col=1,
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


def plot_errors(
    fig, x, y, err, name=None, scatter_kwargs: Optional[Dict[str, Any]] = None, **kwargs
):
    """Scatter plot with data errors."""
    x = np.arange(len(y)) if not isinstance(x, (list, np.ndarray)) else x
    scatter_kwargs = scatter_kwargs or {}
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            error_y={"type": "data", "array": err},
            name=name,
            mode="markers",
            **scatter_kwargs,
        ),
        **kwargs,
    )


def plot_band(
    fig,
    x,
    y_min,
    y_mean,
    y_max,
    name=None,
    scatter_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs,
):
    """Error band plot."""
    if not isinstance(x, (list, np.ndarray)):
        x = np.arange(len(y_mean))

    scatter_kwargs = scatter_kwargs or {}
    scatter_kwargs["opacity"] = scatter_kwargs.get("opacity", 0.8)
    scatter_kwargs["line_color"] = scatter_kwargs.get("line_color", "indigo")
    fig.add_trace(
        go.Scatter(
            x=list(x) + list(x)[::-1],
            y=list(y_max) + list(y_min)[::-1],
            fill="toself",
            mode="lines",
            name=name,
            legendgroup=name,
            **scatter_kwargs,
        ),
        **kwargs,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_mean,
            mode="lines",
            line_color=scatter_kwargs["line_color"],
            showlegend=False,
            legendgroup=name,
        ),
        **kwargs,
    )
