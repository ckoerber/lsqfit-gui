import gvar as gv
import numpy as np
from lsqfit import nonlinear_fit


def process_priors(prior_values, initial_fit):
    
    prior_values = (
        np.array(prior_values, dtype=float).reshape(len(prior_values) // 2, 2).T
    )
    if any(prior_values[1] <= 0):
        raise ValueError("Standard deviations must be larger than zero.")

    flattened_prior_keys = np.concatenate(
        [np.repeat(key, len(initial_fit.prior[key])) if hasattr(initial_fit.prior[key], '__len__') else [key]
        for key in initial_fit.prior
    ])

    prior = {}
    for j, key in enumerate(flattened_prior_keys):
        if key in prior and hasattr(initial_fit.prior[key], '__len__'):
            prior[key] = np.append(prior[key], gv.gvar(prior_values[0][j], prior_values[1][j]))
        elif hasattr(initial_fit.prior[key], '__len__'):
            prior[key] = np.array([gv.gvar(prior_values[0][j], prior_values[1][j])])
        else:
            prior[key] = gv.gvar(prior_values[0][j], prior_values[1][j])

    prior = gv.BufferDict(prior)

    return nonlinear_fit(initial_fit.data, initial_fit.fcn, prior)


def process_meta(meta_array, meta_config):
    """
    """
    return {config["name"]: val for config, val in zip(meta_config, meta_array)}
