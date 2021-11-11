"""Utility functions simplifying plots."""
import numpy as np
import gvar as gv


from lsqfit import nonlinear_fit
from lsqfit._extras import chained_nonlinear_fit, unchained_nonlinear_fit

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


def get_fit_bands(fit):  # add type hint
    """Get x, y_min, y_mean, y_max values for fit."""
    try:
        if isinstance(fit.x, dict):
            x = {
                key: np.linspace(val.min(), val.max(), 100)
                for key, val in fit.x.items()
            }
        else:
            x = np.linspace(fit.x.min(), fit.x.max(), 100)
    except Exception:
        x = fit.x

    if isinstance(fit, (chained_nonlinear_fit, unchained_nonlinear_fit)):
        y = fit.fcn(fit.p)
    elif isinstance(fit, nonlinear_fit):
        y = fit.fcn(fit.x, fit.p)
    else:
        raise ValueError(f"Did not understand fit input of type {type(fit)}")

    m = gv.mean(y)
    s = gv.sdev(y)
    return x, m - s, m, m + s


def get_residuals(fit):
    """Get residuals for fit."""
    if isinstance(fit, (chained_nonlinear_fit, unchained_nonlinear_fit)):
        y_fit = fit.fcn(fit.p)
    elif isinstance(fit, nonlinear_fit):
        y_fit = fit.fcn(fit.x, fit.p)
    else:
        raise ValueError(f"Did not understand fit input of type {type(fit)}")

    if not isinstance(fit.y, (dict, gv.BufferDict)):
        res = (gv.mean(fit.y) - y_fit) / gv.sdev(fit.y)
    else:
        res = {}
        for key, val in y_fit.items():
            res[key] = (gv.mean(fit.y[key]) - val) / gv.sdev(fit.y[key])

    return res


RESIDUALS_DESCRIPTION = r"""The residuals are defined by
$$
\begin{aligned}
    r_i(p) &= \frac{f_i(p) - y_i}{\Delta y_i}\,,&
    \Delta r_i(p) &= \frac{\Delta f_i(p)}{\Delta y_i}
\end{aligned}
$$
where \(f_i(p)\) is the result of the fit at each data location \(i\),
\(y_i\) the corresponding data values, \(p\) the posterior,
and \(\Delta\) denotes the standard deviation for respective objects.

In other words, if central values distribute around one, the \(\chi^2\) per d.o.f.
will be close to one; if errorbars are close to one,
the posterior uncertainty mirrors the data uncertainty.
"""
