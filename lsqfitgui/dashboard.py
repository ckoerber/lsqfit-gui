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
    set_page_config,
    container,
    expander,
    columns,
    warning,
    stop,
)
from plotly.subplots import make_subplots
from scipy.stats import norm
from pandas import DataFrame
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


def add_gvar_widget(parent, name: str, gv: GVar):
    """Adds widget to parent for given gvar."""
    m, s = gv.mean, gv.sdev
    parent.subheader(name)
    col1, col2 = parent.columns(2)
    mean = float(col1.text_input(label="mean", value=str(m), key=f"{name}_mean"))
    sdev = float(col2.text_input(label="sdev", value=str(s), key=f"{name}_sdev"))

    if sdev <= 0:
        warning(f"Stanard deviation for {name} must be larger than zero.")
        stop()

    return mean, sdev


def sidebar_from_prior(prior: BufferDict) -> BufferDict:
    """Creates streamlit sidebar from prior."""
    sidebar.header("Prior")
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
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["x"].values,
            y=data["y"].values,
            error_y={"type": "data", "array": data["y_err"].values},
            name="Data",
            mode="markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=list(x_fit) + list(x_fit)[::-1],
            y=list(y_fit_max) + list(y_fit_min)[::-1],
            fill="toself",
            mode="lines",
            line_color="indigo",
            name="Fit",
            opacity=0.8,
            legendgroup="fit",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_fit,
            y=y_fit_mean,
            mode="lines",
            line_color="indigo",
            showlegend=False,
            legendgroup="fit",
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

    fig.update_layout(
        template="plotly_white", font={"size": 16}, hoverlabel={"font_size": 16},
    )
    return fig, r_fig


COLORS = {"prior": "blue", "posterior": "green"}


def get_p2p_fig(fit):
    fig = make_subplots(
        rows=len(fit.p), shared_xaxes=False, subplot_titles=list(fit.p.keys())
    )
    for n, (key, prior) in enumerate(fit.prior.items()):
        posterior = fit.p[key]

        for which, val in [("prior", prior), ("posterior", posterior)]:
            x = np.linspace(val.mean - 3 * val.sdev, val.mean + 3 * val.sdev, 200)
            y = norm(val.mean, val.sdev).pdf(x)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    fill="tozeroy",
                    name=which,
                    line_color=COLORS[which],
                    showlegend=n == 0,
                ),
                row=n + 1,
                col=1,
            )
    return fig


def init_dasboard(input_fit: nonlinear_fit):
    """Initializes dashboard from fit."""
    set_page_config(layout="wide")
    title("lsqfit-gui")
    with expander("Show fit function", expanded=False):
        header("Fit function")
        latex("f(x) = " + parse_fit_fcn(input_fit))

    prior = sidebar_from_prior(input_fit.prior)
    fit = nonlinear_fit(input_fit.data, input_fit.fcn, prior)

    with expander("Show details", expanded=True):
        header("Fit details")
        code(fit.format(maxline=True), language=None)

    header("Plots")
    with expander("Show fit", expanded=True):
        subheader("Data vs fit")
        fig_fit, fig_residuals = get_fit_fig(fit)
        plotly_chart(fig_fit, use_container_width=True)

    with expander("Show residuals", expanded=False):
        subheader("Residuals")
        plotly_chart(fig_residuals, use_container_width=True)

    with expander("Show posterior vs prior", expanded=False):
        header("Posteriors and priors")
        plotly_chart(get_p2p_fig(fit), use_container_width=True)
