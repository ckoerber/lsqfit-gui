"""Plotting routines associated with fit objects."""
from typing import Callable, Optional

import gvar as gv

from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

from lsqfitgui.plot.util import get_fit_bands, get_residuals
from lsqfitgui.plot.uncertainty import plot_errors, plot_band


LOG_MENU = dict(
    type="dropdown",
    direction="down",
    y=1.2,
    x=0,
    xanchor="left",
    buttons=list(
        [
            dict(
                args=[{"yaxis": {"type": "linear"}}],
                label="Linear Scale",
                method="relayout",
            ),
            dict(
                args=[{"yaxis": {"type": "log"}}], label="Log Scale", method="relayout",
            ),
        ]
    ),
)


def plot_fit(fit, fig: Optional[Figure] = None, fcn: Optional[Callable] = None, y = None): # add type hint
    """Plot data and fit error bands."""
    x_fit, y_min_fit, y_mean_fit, y_max_fit = get_fit_bands(fit, fcn=fcn)

    if not isinstance(fit.y, (dict, gv.BufferDict)):
        fig = fig or Figure()

        if y is None and fcn is None: # show y
            plot_errors(fig, fit.x, gv.mean(fit.y), gv.sdev(fit.y), name="Data")
        elif y is not None: # show transformed y
            plot_errors(fig, fit.x, gv.mean(y), gv.sdev(y), name="Data")

        if (
            (fcn is not None) # fcn specified => show plot fcn
            or (y is None) # y is None => using fit.y => show fit; 
            or (y == fit.y).all() # y=fit.y as an argument => show fit
        ):
            plot_band(fig, x_fit, y_min_fit, y_mean_fit, y_max_fit, name="Fit")

    else:
        fig = fig or make_subplots(
            cols=1, rows=len(fit.y), subplot_titles=list(fit.y.keys())
        )

        for n, (key, yy) in enumerate(fit.y.items()):
            if y is None and fcn is None: # show y 
                plot_errors(
                    fig,
                    fit.x[key] if isinstance(fit.x, dict) else fit.x,
                    gv.mean(yy),
                    gv.sdev(yy),
                    name=f"{key} data",
                    row=n + 1,
                    col=1,
                )
            elif y is not None: # show transformed y
                plot_errors(
                    fig,
                    fit.x[key] if isinstance(fit.x, dict) else fit.x,
                    gv.mean(y[key]),
                    gv.sdev(y[key]),
                    name=f"{key} data",
                    row=n + 1,
                    col=1,
                )

            if (
                (fcn is not None) # fcn specified => show plot fcn
                or (y is None) # y is None => using fit.y => show fit; 
                or all([(y[key] == fit.y[key]).all() for key in fit.y]) # y=fit.y as an argument => show fit
            ):
                plot_band(
                    fig,
                    x_fit[key] if isinstance(x_fit, dict) else x_fit,
                    y_min_fit[key],
                    y_mean_fit[key],
                    y_max_fit[key],
                    name=f"{key} fit",
                    row=n + 1,
                    col=1,
                )

        fig.update_layout(height=len(fit.y) * 300)

    fig.update_layout(
        template="plotly_white",
        font={"size": 16},
        hoverlabel={"font_size": 16},
        updatemenus=[LOG_MENU]
        if not isinstance(fit.y, (dict, gv.BufferDict))
        else None,
    )
    return fig


def plot_residuals(fit, fig: Optional[Figure] = None):
    """Plot fit residuals."""
    residuals = get_residuals(fit)

    if not isinstance(fit.y, (dict, gv.BufferDict)):
        fig = fig or Figure()
        plot_errors(fig, fit.x, gv.mean(residuals), gv.sdev(residuals))
    else:
        fig = fig or make_subplots(
            cols=1, rows=len(fit.y), subplot_titles=list(fit.y.keys())
        )
        for n, (key, yy) in enumerate(fit.y.items()):
            xx = fit.x[key] if isinstance(fit.x, dict) else fit.x
            plot_errors(
                fig,
                xx,
                gv.mean(residuals[key]),
                gv.sdev(residuals[key]),
                name=key,
                row=n + 1,
                col=1,
            )

        fig.update_layout(height=len(fit.y) * 300)
    fig.add_hline(0, line={"color": "black"})

    fig.update_layout(
        template="plotly_white",
        font={"size": 16},
        hoverlabel={"font_size": 16},
        # updatemenus=[LOG_MENU],
    )
    return fig
