"""Example application of lsqfit-gui on a "basic fit".

This fit uses array arguments and single-argument data.
"""
import numpy as np
import gvar as gv
import lsqfit

from lsqfitgui import run_server


XX = np.arange(0, 4, 1.0)
YY = gv.gvar(len(XX) * ["1(1)"])


def fcn(p, x=XX):
    return p[0] + x * p[1]


def main():
    """Run the fit gui."""
    prior = gv.gvar(2 * ["0.5(5)"])
    fit = lsqfit.nonlinear_fit(data=YY, prior=prior, fcn=fcn)

    run_server(fit=fit)


if __name__ == "__main__":
    main()
