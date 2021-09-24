#!/usr/bin/env python3
# coding: utf-8
"""Module which provides example interface to lsqfitgui."""
import gvar as gv
import numpy as np
import lsqfit
import os

np.random.seed(42)


def fcn(x, p):
    """Returns polyinomial function.

    Arguemnts:
        x: Indepdent variable (array)
        p: Paramters. Keys must be `a{n}` where n can be arbitrary.
    """
    return sum([an * x ** int(key[1:]) for key, an in p.items()])


def generate_data(n_poly: int = 5, n_data: int = 50):
    """Generate synthetic data for fit."""
    a0 = np.random.normal(size=n_poly)
    a0 = gv.gvar(a0, a0 * np.random.uniform(0.1, 0.3, size=n_poly))
    x = np.linspace(0, 2, n_data)
    y = fcn(x, {f"a{n}": val for n, val in enumerate(a0)})
    y += gv.gvar(
        np.zeros(n_data), gv.mean(y) * np.random.uniform(0.05, 0.1, size=n_data)
    )
    return (x, y)


def generate_prior(n_poly: int = 5):
    """Generate prior distribution for fit."""
    return {f"a{n}": gv.gvar(0, n + 1) for n in range(n_poly)}


def generate_fit(**meta):
    """Generate a fit for specified meta information."""
    data = generate_data()
    prior = generate_prior(n_poly=meta["n_poly"])
    fit = lsqfit.nonlinear_fit(data=data, fcn=fcn, prior=prior)
    fit.meta = meta
    return fit


def main():
    """Create an output pickled fit file `fit.p`."""
    outfile = os.path.join(os.path.dirname(__file__), "fit.p")
    fit = generate_fit(n_poly=5)
    gv.dump(fit, outputfile=outfile)


if __name__ == "__main__":
    main()
