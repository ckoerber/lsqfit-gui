"""Validation functions used for checking fit arguments."""
from typing import Optional, Callable, Dict, List

from numpy import eye, allclose, ndarray
from gvar import evalcorr, BufferDict

from lsqfit import nonlinear_fit
from lsqfit._extras import unchained_nonlinear_fit

from lsqfitgui.util.models import (
    lsqfit_from_multi_model_fit,
    lsqfit_from_multi_model_fit_wrapper,
)
from lsqfitgui.util.prior import fit_with_prior_dict, fit_with_prior_dict_wrapper
from lsqfitgui.util.data import fit_with_xy, fit_with_xy_wrapper
from lsqfitgui.validation.exceptions import SetupException


def process_fit(
    fit: Optional[nonlinear_fit] = None,
    fit_setup_function: Optional[Callable] = None,
    fit_setup_kwargs: Optional[Dict] = None,
    meta_config: Optional[List[Dict]] = None,
):
    """Validate input arguments and raise proper error messages for setting up the fit.

    Raises:
        SetupException: In case the input arguments are unexpected.
    """
    fit_setup_kwargs = fit_setup_kwargs or {}

    if fit is None and fit_setup_function is None:
        raise SetupException(
            [
                ValueError(
                    "You must either specify the fit or fit setup function"
                    " to initialize the GUI."
                )
            ]
        )
    elif fit_setup_function is not None:
        try:
            initial_fit = fit_setup_function(**fit_setup_kwargs)
        except Exception as e:
            raise SetupException([e])
    else:
        initial_fit = fit

    # Check if multi model fit and adjust objects
    if isinstance(initial_fit, unchained_nonlinear_fit):
        try:
            initial_fit = lsqfit_from_multi_model_fit(initial_fit)
            if fit_setup_function is not None:
                fit_setup_function = lsqfit_from_multi_model_fit_wrapper(
                    fit_setup_function
                )
                initial_fit = fit_setup_function(**fit_setup_kwargs)
        except Exception as e:
            raise SetupException([e])

    # Check if data is a tuple of two
    if not isinstance(initial_fit.data, tuple):
        try:
            initial_fit = fit_with_xy(initial_fit)
            if fit_setup_function is not None:
                fit_setup_function = fit_with_xy_wrapper(fit_setup_function)
                initial_fit = fit_setup_function(**fit_setup_kwargs)
        except Exception as e:
            raise SetupException([e])

    # Check if prior is a dict and if not adjust objects
    if not isinstance(initial_fit.prior, (dict, BufferDict)):
        if not isinstance(initial_fit.prior, (list, ndarray)):
            raise SetupException(
                [TypeError("Prior must be either a dict or an array.")]
            )
        try:
            initial_fit = fit_with_prior_dict(initial_fit)
            if fit_setup_function is not None:
                fit_setup_function = fit_with_prior_dict_wrapper(fit_setup_function)
                initial_fit = fit_setup_function(**fit_setup_kwargs)
        except Exception as e:
            raise SetupException([e])

    # Check prior correlations
    if not allclose(
        evalcorr(initial_fit.prior.flatten()), eye(len(initial_fit.prior.flatten())),
    ):
        raise SetupException(
            [NotImplementedError("Prior of original fit contains correlations.")]
        )

    return initial_fit, fit_setup_function


def validate_fit(fit: nonlinear_fit):
    """Assert fit is in expected shape."""
