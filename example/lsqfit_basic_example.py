"""Example application of lsqfit-gui on a "basic fit" from the lsqfit documentation.

See also https://lsqfit.readthedocs.io/en/latest/overview.html#basic-fits
"""

import lsqfitgui
from lsqfitgui.plot.uncertainty import wrap_plot_gvar, plot_gvar
import lsqfit
import numpy as np
import gvar as gv

"""
# An even more basic example; comment-out the other main() instead
def main():
    x, y = make_data()              # collect fit data
    p0 = None                       # make larger fits go faster (opt.)
    prior = make_prior(nexp=5)
    fit = lsqfit.nonlinear_fit(data=(x, y), fcn=fcn, prior=prior, p0=p0)

    lsqfitgui.run_server(fit)
"""


def main():
    x, y = make_data()
    y_eff_mass = np.array([])
    dx = np.roll(x, -1) - x
    y_eff_mass = np.log(y / np.roll(y, -1)) / dx
    y_eff_wf = np.exp(y_eff_mass * x) * y

    lsqfitgui.run_server(
        fit_setup_function=generate_fit,
        fit_setup_kwargs={"n_exp": 4},
        meta_config=[
            {"name": "n_exp", "type": "number", "min": 1, "max": 10, "step": 1}
        ],
        additional_plots=[
            {
                "name": "Effective mass",
                "fcn": eff_mass,
                "kwargs": {},  # passed to eff_mass function directly
                "static_plot_gvar": {  # calls plot_gvar on the same figure
                    "x": x,
                    "y": y_eff_mass,
                    "kind": "errorbars",
                    "scatter_kwargs": {"name": "Data"},
                },
            },
            {
                "name": "Effective WF",
                # "fcn": eff_wf, # both would do the same thing
                "fcn": plot_eff_wf,
                "kwargs": {},  # passed to eff_mass function directly
                "static_plot_gvar": {  # calls plot_gvar on the same figure
                    "x": x,
                    "y": y_eff_wf,
                    "kind": "errorbars",
                    "scatter_kwargs": {"name": "Data"},
                },
            },
        ],
    )


def generate_fit(**meta):
    """Generate a fit for specified meta information."""
    x, y = make_data()  # collect fit data
    p0 = None  # make larger fits go faster (opt.)
    prior = make_prior(nexp=meta["n_exp"])
    fit = lsqfit.nonlinear_fit(data=(x, y), fcn=fcn, prior=prior, p0=p0)
    fit.meta = meta
    return fit


def fcn(x, p):
    """Multi exponential fit function.

    `sum([a_i * exp(-E_i * x)])`

    Arguemnts of prior p:
        a: array of a[i]s
        E: array of E[i]s
    """
    return np.array(sum(ai * np.exp(-Ei * x) for ai, Ei in zip(p["a"], p["E"])))


@wrap_plot_gvar(kind="band", scatter_kwargs={"opacity": 0.5, "name": "Fit"})
def eff_mass(x, p):
    return np.log(fcn(x, p) / fcn(x + 1, p))


@wrap_plot_gvar(kind="band", scatter_kwargs={"opacity": 0.5, "name": "Fit"})
def eff_wf(x, p):
    return np.exp(np.log(fcn(x, p) / fcn(x + 1, p)) * x) * fcn(x, p)


# The above call does effectively the below code


def plot_eff_wf(fit):
    ff = fcn(fit.x, fit.p)
    return plot_gvar(
        fit.x,
        np.exp(np.log(ff / fcn(fit.x + 1, fit.p)) * fit.x) * ff,
        kind="band",
        scatter_kwargs={"opacity": 0.5, "name": "Fit"},
    )


def make_prior(nexp):  # make priors for fit parameters
    prior = gv.BufferDict()  # any dictionary works
    prior["a"] = [gv.gvar(0.5, 0.4) for i in range(nexp)]
    prior["E"] = [gv.gvar(i + 1, 0.4) for i in range(nexp)]
    return prior


def make_data():  # assemble fit data
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
    return x, gv.gvar(ymean, ycov)


if __name__ == "__main__":
    main()
