"""Plotting shortcuts for plotly error plots and bands."""
from typing import Optional

import numpy as np
import gvar as gv

import plotly.graph_objects as go


def plot_gvar(x, y, fig: Optional[go.Figure], kind: str = "data", **kwargs):
    """Plots gvars."""
    fig = fig or go.Figure()
    mean = gv.mean(y)
    sdev = gv.sdev(y)
    return (
        plot_errors(fig, x, mean, sdev, **kwargs)
        if kind == "data"
        else plot_band(fig, x, mean - sdev, mean, mean + sdev, **kwargs)
    )


def plot_errors(fig, x, y, err, name=None, **kwargs):
    """Scatter plot with data errors."""
    x = np.arange(len(y)) if not isinstance(x, (list, np.ndarray)) else x
    fig.add_trace(
        go.Scatter(
            x=x, y=y, error_y={"type": "data", "array": err}, name=name, mode="markers",
        ),
        **kwargs,
    )


def plot_band(fig, x, y_min, y_mean, y_max, name=None, **kwargs):
    """Error band plot."""
    if not isinstance(x, (list, np.ndarray)):
        x = np.arange(len(y_mean))
    fig.add_trace(
        go.Scatter(
            x=list(x) + list(x)[::-1],
            y=list(y_max) + list(y_min)[::-1],
            fill="toself",
            mode="lines",
            line_color="indigo",
            name=name,
            opacity=0.8,
            legendgroup=name,
        ),
        **kwargs,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_mean,
            mode="lines",
            line_color="indigo",
            showlegend=False,
            legendgroup=name,
        ),
        **kwargs,
    )
