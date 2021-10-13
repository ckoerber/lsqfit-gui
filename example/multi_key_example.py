"""Example script for fit with multiple keys.

See also https://github.com/ckoerber/lsqfit-gui/issues/10
"""
import lsqfit
import gvar as gv
import numpy as np

from lsqfitgui import run_server
from lsqfitgui.plot.uncertainty import wrap_plot_function

XX = dict(
    d1=np.array([1, 2, 3, 4]),
    d2=np.array([1, 2, 3, 4]),
    d3=np.array([1, 2, 3, 4]),
    d4=np.array([1, 2, 3, 4]),
    d5=np.array([5, 6, 7, 8]),
)

YY = dict(
    d1=["1.154(10)", "2.107(16)", "3.042(22)", "3.978(29)"],
    d2=["0.692(10)", "1.196(16)", "1.657(22)", "2.189(29)"],
    d3=["0.107(10)", "0.030(16)", "-0.027(22)", "-0.149(29)"],
    d4=["0.002(10)", "-0.197(16)", "-0.382(22)", "-0.627(29)"],
    d5=["1.869(10)", "2.198(16)", "2.502(22)", "2.791(29)"],
)
PRIOR = gv.gvar(dict(a="0(1)", s1="0(1)", s2="0(1)", s3="0(1)", s4="0(1)", s5="0(1)"))


def fitfcn(x, p):
    """Return linear fit function.

    $$f(x; a, s_n) = a + s_n * x$$
    """
    return {key: p["a"] + p[f"s{key[1:]}"] * x[key] for key in x}


@wrap_plot_function(kind="band", name="Squared", opacity=0.5)
def squared(x, p):
    return {key: (p["a"] + p[f"s{key[1:]}"] * x[key]) ** 2 for key in x}


def get_fit():
    """Return fit object."""
    return lsqfit.nonlinear_fit(data=(XX, YY), fcn=fitfcn, prior=PRIOR)


def main():
    y_squared = {key: gv.gvar(YY[key]) ** 2 for key in YY}
    """Run lsqfitgui server for multi-linear fit."""
    run_server(
        get_fit(),
        additional_plots=[
            {"name": "Squared", "fcn": squared, "y-data": y_squared, "x-data": XX,}
        ],
    )


if __name__ == "__main__":
    main()
