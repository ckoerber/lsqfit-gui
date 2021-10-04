import gvar as gv
import numpy as np
from lsqfit import nonlinear_fit


def process_priors(prior_values, initial_fit):
    prior_values = (
        np.array(prior_values, dtype=float).reshape(len(prior_values) // 2, 2).T
    )
    if any(prior_values[1] <= 0):
        raise ValueError("Standard deviations must larger zero.")
    prior = {
        key: val
        for key, val in zip(initial_fit.p, gv.gvar(prior_values[0], prior_values[1]))
    }
    return nonlinear_fit(initial_fit.data, initial_fit.fcn, prior)


def process_meta(meta_array, meta_config):
    """
    """
    return {config["name"]: val for config, val in zip(meta_config, meta_array)}
