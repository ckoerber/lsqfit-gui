"""Utility functions simplifying plots."""
import numpy as np
import gvar as gv


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

    y = fit.fcn(x, fit.p)

    m = gv.mean(y)
    s = gv.sdev(y)
    return x, m - s, m, m + s


def get_residuals(fit):
    """Get residuals for fit."""
    y_fit = fit.fcn(fit.x, fit.p)

    if not isinstance(fit.y, (dict, gv.BufferDict)):
        res = (gv.mean(fit.y) - y_fit) / gv.sdev(fit.y)
    else:
        res = {}
        for key, val in y_fit.items():
            res[key] = (gv.mean(fit.y[key]) - val) / gv.sdev(fit.y[key])

    return res
