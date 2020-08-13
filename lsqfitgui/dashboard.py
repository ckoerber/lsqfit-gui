"""Initializes dashboard from fit."""
import re
import sympy
from lsqfit import nonlinear_fit
from gvar import BufferDict, gvar
import gvar as gv
from gvar._gvarcore import GVar
from streamlit import (
    sidebar,
    title,
    text,
    code,
    latex,
    header,
    subheader,
    plotly_chart,
    checkbox,
)
from pandas import DataFrame
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


def add_gvar_widget(parent, name: str, gv: GVar):
    """Adds widget to parent for given gvar."""
    m, s = gv.mean, gv.sdev
    parent.subheader(name)
    mean = parent.number_input(label="mean", value=m, step=s / 3, key=f"{name}_mean")
    sdev = parent.number_input(label="sdev", value=s, step=s / 3, key=f"{name}_sdev")
    return mean, sdev


def sidebar_from_prior(prior: BufferDict) -> BufferDict:
    """Creates streamlit sidebar from prior."""
    pprior = BufferDict()
    for key, value in prior.items():
        if hasattr(value, "__iter__"):
            raise NotImplementedError("Prior array values not supported yet.")
        pprior[key] = gvar(add_gvar_widget(sidebar, key, value))
    return pprior


def parse_fit_fcn(fit: nonlinear_fit) -> str:
    """Parses the fit function and posteriror to latex label."""
    expressions = {}
    values = {}
    for key, val in fit.p.items():
        if hasattr(val, "__iter__"):
            expr = sympy.symbols(" ".join([f"{key}{n}" for n, el in enumerate(val)]))
        else:
            expr = sympy.Symbol(key)

        expressions[key] = expr

        if hasattr(expr, "__iter__"):
            for ee, vv in zip(expr, val):
                values[sympy.latex(ee)] = vv
        else:
            values[sympy.latex(expr)] = val

    f_expr = fit.fcn(
        x=sympy.Symbol("x"), p={key: expr for key, expr in expressions.items()}
    )

    s = sympy.latex(f_expr)
    return re.sub(r"\+\s+\-", "-", s)


def generate_data(fit) -> DataFrame:
    pass


def get_fit_bands(fit):
    x = np.linspace(fit.x.min(), fit.x.max(), 100)
    y = fit.fcn(x, fit.p)
    m = gv.mean(y)
    s = gv.sdev(y)
    return x, m - s, m, m + s


def get_residuals(fit):
    y_fit = fit.fcn(fit.x, fit.p)
    return (gv.mean(fit.y) - y_fit) / gv.sdev(fit.y)


def get_fit_fig(fit):
    data = DataFrame(
        data=np.transpose([fit.x, gv.mean(fit.y), gv.sdev(fit.y)]),
        columns=["x", "y", "y_err"],
    )
    x_fit, y_fit_min, y_fit_mean, y_fit_max = get_fit_bands(fit)
    fig = px.scatter(data, x="x", y="y", error_y="y_err")
    fig.add_trace(
        go.Scatter(x=x_fit, y=y_fit_min, fill=None, mode="lines", line_color="indigo",)
    )
    fig.add_trace(
        go.Scatter(
            x=x_fit,
            y=y_fit_min,
            fill="tonexty",  # fill area between trace0 and trace1
            mode="lines",
            line_color="indigo",
        )
    )
    residuals = get_residuals(fit)
    data = DataFrame(
        data=np.transpose([fit.x, gv.mean(residuals), gv.sdev(residuals)]),
        columns=["x", "r", "r_err"],
    )
    r_fig = px.scatter(data, x="x", y="r", error_y="r_err")
    r_fig.add_trace(
        go.Scatter(x=fit.x, y=np.zeros(len(fit.x)), mode="lines", line_color="black")
    )
    return fig, r_fig


def init_dasboard(fit: nonlinear_fit):
    """Initializes dashboard from fit."""
    title("lsqfit-gui")
    header("Fit function")
    latex("f(x) = " + parse_fit_fcn(fit))

    prior = sidebar_from_prior(fit.prior)
    fit = nonlinear_fit(fit.data, fit.fcn, prior)

    header("Plot")
    subheader("Data vs fit")
    fig_fit, fig_residuals = get_fit_fig(fit)
    plotly_chart(fig_fit)
    show_residuals = checkbox("Show residuals", value=False)
    if show_residuals:
        subheader("Residuals")
        plotly_chart(fig_residuals)

    show_details = checkbox("Show details", value=True)
    if show_details:
        header("Fit details")
        code(fit.format(maxline=True), language=None)
