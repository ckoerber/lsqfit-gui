"""Functions for parsing sidebar form values into python objects."""
import re
import gvar as gv
from lsqfit import nonlinear_fit


def process_priors(prior_flat, initial_fit):
    """Process prior input array into fit object."""
    if any(
        [float(val) <= 0 for key, val in prior_flat.items() if key.endswith("sdev")]
    ):
        raise ValueError("Standard deviations must be larger than zero.")

    prior = {}
    for key, val in initial_fit.prior.items():
        if hasattr(val, "__len__"):
            nmax = len(
                [k for k in prior_flat if re.match(f"{key}__array_[0-9]+-mean", k)]
            )
            prior[key] = gv.gvar(
                [prior_flat[f"{key}__array_{n}-mean"] for n in range(nmax)],
                [prior_flat[f"{key}__array_{n}-sdev"] for n in range(nmax)],
            )
        else:
            prior[key] = gv.gvar(prior_flat[f"{key}-mean"], prior_flat[f"{key}-sdev"])

    fit = nonlinear_fit(initial_fit.data, initial_fit.fcn, prior)

    for attr in ["models", "meta"]:
        if hasattr(initial_fit, attr):
            setattr(fit, attr, getattr(initial_fit, attr))

    return fit


def process_meta(meta_array, meta_config):
    """Parse meta form input into dictionary shape using meta config name values."""
    return {config["name"]: val for config, val in zip(meta_config, meta_array)}
