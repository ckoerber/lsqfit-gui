"""Functions for parsing sidebar form values into python objects."""
from typing import Dict, List, Any, Optional, Callable

import re
import gvar as gv
from lsqfit import nonlinear_fit


def process_priors(prior_flat, initial_fit):
    """Process prior input array into fit object."""
    if any([float(val) <= 0 for key, val in prior_flat.items() if key.endswith("sdev")]):
        raise ValueError("Standard deviations must be larger than zero.")

    prior = {}
    for key, val in initial_fit.prior.items():
        if hasattr(val, "__len__"):
            nmax = len([k for k in prior_flat if re.match(f"{key}__array_[0-9]+-mean", k)])
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


def process_meta(
    meta_array: Optional[List[Any]],
    meta_config: Optional[List[Dict[str, Any]]] = None,
    meta_validator: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Parse meta form input into dictionary shape using meta config name values."""
    # for python 3.10+ this will be zip(*, strict=False)
    if not meta_array and not meta_config:
        return {}
    elif meta_array and not meta_config:
        raise TypeError("Improperly configured. Received meta config values but no meta config.")
    elif meta_config and not meta_array:
        raise TypeError("Improperly configured. Received meta configs but no values.")
    else:
        assert isinstance(meta_config, list)
        assert isinstance(meta_array, list)
        if len(meta_config) != len(meta_array):
            raise ValueError(
                "Improperly configured."
                " Meta config options does not have the same number of values recieved."
            )
        meta = {config["name"]: val for config, val in zip(meta_config, meta_array)}
        if meta_validator is not None:
            meta = meta_validator(meta)
        return meta
