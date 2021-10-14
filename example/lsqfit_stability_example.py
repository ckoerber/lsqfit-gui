"""Example application of lsqfit-gui on a "basic fit" from the lsqfit documentation.

See also https://lsqfit.readthedocs.io/en/latest/overview.html#basic-fits
"""
from itertools import product

import numpy as np
import pandas as pd

import gvar as gv
import lsqfit

import plotly.express as px

import lsqfitgui


T_MIN_RANGE = range(0, 4)
T_MAX_RANGE = range(8, 9)
N_EXP_RANGE = range(2, 5)
RANGE_PRODUCT = list(product(T_MIN_RANGE, T_MAX_RANGE, N_EXP_RANGE))


def k2s(*args) -> str:
    """Maps multiple arguments to a string.

    Needed since gui labels need to be strings.
    """
    return ", ".join(map(str, args))


def generate_fit():
    """Generate a fit for specified meta information."""
    xx = {}
    yy = gv.BufferDict()
    prior = gv.BufferDict()
    p0 = None
    for t_min, t_max, n_exp in RANGE_PRODUCT:
        kkey = k2s(t_min, t_max, n_exp)
        xx[kkey], yy[kkey] = make_data(t_min=t_min, t_max=t_max)

        args = (t_min, t_max, n_exp)
        for key, val in make_prior(nexp=n_exp).items():
            prior[k2s(*args, key)] = val

    fit = lsqfit.nonlinear_fit(data=(xx, yy), fcn=fcn, prior=prior, p0=p0,)
    return fit


def fcn(x, p, individual_priors: bool = False):
    """Multi exponential fit function.

    `sum([a_i * exp(-E_i * x)])`

    Arguemnts of prior p:
        a: array of a[i]s
        E: array of E[i]s
    """
    out = {}
    for args in RANGE_PRODUCT:

        a = p[k2s(*args, "a")]
        E = p[k2s(*args, "E")]
        xx = x[k2s(*args)]

        out[k2s(*args)] = np.array(sum([ai * np.exp(-Ei * xx) for ai, Ei in zip(a, E)]))
    return out


def make_prior(nexp):  # make priors for fit parameters
    prior = gv.BufferDict()  # any dictionary works
    prior["a"] = [gv.gvar(0.5, 0.4) for i in range(nexp)]
    prior["E"] = [gv.gvar(i + 1, 0.4) for i in range(nexp)]
    return prior


def make_data(t_min=0, t_max=8):  # assemble fit data

    if t_min < 0 or t_max > 8:
        raise ValueError("t rannge not valid")
    # fmt: off
    x = np.array([  5.,   6.,   7.,   8.,   9.,  10.,  12.,  14.])
    ymean = np.array(
       [  4.5022829417e-03,   1.8170543788e-03,   7.3618847843e-04,
          2.9872730036e-04,   1.2128831367e-04,   4.9256559129e-05,
          8.1263644483e-06,   1.3415253536e-06]
       )
    ycov = np.array(
       [[ 2.1537808808e-09,   8.8161794696e-10,   3.6237356558e-10,
          1.4921344875e-10,   6.1492842463e-11,   2.5353714617e-11,
          4.3137593878e-12,   7.3465498888e-13],
       [  8.8161794696e-10,   3.6193461816e-10,   1.4921610813e-10,
          6.1633547703e-11,   2.5481570082e-11,   1.0540958082e-11,
          1.8059692534e-12,   3.0985581496e-13],
       [  3.6237356558e-10,   1.4921610813e-10,   6.1710468826e-11,
          2.5572230776e-11,   1.0608148954e-11,   4.4036448945e-12,
          7.6008881270e-13,   1.3146405310e-13],
       [  1.4921344875e-10,   6.1633547703e-11,   2.5572230776e-11,
          1.0632830128e-11,   4.4264622187e-12,   1.8443245513e-12,
          3.2087725578e-13,   5.5986403288e-14],
       [  6.1492842463e-11,   2.5481570082e-11,   1.0608148954e-11,
          4.4264622187e-12,   1.8496194125e-12,   7.7369196122e-13,
          1.3576009069e-13,   2.3914810594e-14],
       [  2.5353714617e-11,   1.0540958082e-11,   4.4036448945e-12,
          1.8443245513e-12,   7.7369196122e-13,   3.2498644263e-13,
          5.7551104112e-14,   1.0244738582e-14],
       [  4.3137593878e-12,   1.8059692534e-12,   7.6008881270e-13,
          3.2087725578e-13,   1.3576009069e-13,   5.7551104112e-14,
          1.0403917951e-14,   1.8976295583e-15],
       [  7.3465498888e-13,   3.0985581496e-13,   1.3146405310e-13,
          5.5986403288e-14,   2.3914810594e-14,   1.0244738582e-14,
          1.8976295583e-15,   3.5672355835e-16]]
       )
    # fmt: on
    return x[t_min:t_max], gv.gvar(ymean, ycov)[t_min:t_max]


def plot_stability(fit, **kwargs):
    """Creates a stability plot."""
    delta_n_exp = N_EXP_RANGE[-1] - N_EXP_RANGE[0]

    data = []
    e0s = []
    for t_min, t_max, n_exp in RANGE_PRODUCT:
        e0 = fit.p[k2s(t_min, t_max, n_exp, "E")][0]
        data.append(
            {
                "t_min": t_min
                + (n_exp - N_EXP_RANGE[0] - delta_n_exp / 2) / delta_n_exp * 0.1,
                "t_max": str(t_max),
                "n_exp": str(n_exp),
                "E0 mean": e0.mean,
                "E0 sdev": e0.sdev,
            }
        )
        e0s.append(e0)
    df = pd.DataFrame(data)

    fig = px.scatter(
        df,
        x="t_min",
        y="E0 mean",
        error_y="E0 sdev",
        color="n_exp",
        symbol="n_exp",
        facet_row="t_max",
    )
    mean = gv.mean(e0s).mean()
    sdev = np.sqrt(gv.mean(e0s).std(ddof=1) ** 2 + gv.sdev(e0s).mean() ** 2)
    fig.add_hrect(mean - sdev, mean + sdev, opacity=0.5, fillcolor="gray")
    fig.add_hline(mean, line_color="gray")
    return fig


def main():
    """Run the stability plot server."""
    lsqfitgui.run_server(
        fit=generate_fit(),
        additional_plots=[{"name": "Stability plot", "fcn": plot_stability}],
    )


if __name__ == "__main__":
    main()
