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
                args=[{"yaxis": {"type": "log"}}],
                label="Log Scale",
                method="relayout",
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


def get_residuals(fit, with_prior: bool = False):
    """Get residuals for fit."""
    # this is a flat array; this removes prior information
    residuals = get_weighted_residuals_fit(fit)[: -len(fit.prior.flatten())]

    if isinstance(fit.y, (dict, gv.BufferDict)):
        r = gv.BufferDict()
        n = 0
        for key, val in fit.y.items():
            nn = n + len(val)
            r[key] = residuals[n:nn]
            n = nn
        residuals = r

    return residuals


def get_weighted_residuals_fit(fit):

    target = np.concatenate([fit.fcn(fit.x, fit.p).flat, fit.p.flat])
    base = np.concatenate([fit.y.flat, fit.prior.flat])

    return get_weighted_residuals(target, base, fit.fdata.inv_wgts)


def get_weighted_residuals(target, base, inv_wgts):
    """Approach of including correlations in residuals plot.

    Follows
    https://github.com/gplepage/lsqfit/blob/1f1a8fdac5801c1cfec14a8d37bd23b056764bdf/src/lsqfit/__init__.py#L1897
    and
    https://github.com/gplepage/lsqfit/blob/1f1a8fdac5801c1cfec14a8d37bd23b056764bdf/src/lsqfit/_utilities.pyx#L59
    """

    delta = (target - gv.mean(base)).flatten()
    ans = np.zeros(sum(len(wgts) for _, wgts in inv_wgts), dtype=float) * gv.gvar(0, 0)

    iw, wgts = inv_wgts[0]
    i1 = 0
    i2 = len(iw)
    if i2 > 0:
        ans[i1:i2] = wgts * delta[iw]

    for iw, wgt in inv_wgts[1:]:
        i1 = i2
        i2 += len(wgt)
        ans[i1:i2] += delta[iw] * wgt if len(wgt.shape) == 1 else wgt @ delta[iw]

    return ans


get_residuals.description = r"""The residuals are defined by
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
