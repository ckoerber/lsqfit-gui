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
    try:
        if isinstance(fit.x, dict):
            x = {
                key: np.linspace(val.min(), val.max(), 100)
                for key, val in fit.x.items()
            }
        else:
            x = np.linspace(fit.x.min(), fit.x.max(), 100)
    except Exception:
        x = fit.x
    y = fit.fcn(x, fit.p)
    m = gv.mean(y)
    s = gv.sdev(y)
    return x, m - s, m, m + s


def get_residuals(fit):
    y_fit = fit.fcn(fit.x, fit.p)

    if not isinstance(fit.y, (dict, gv.BufferDict)):
        res = (gv.mean(fit.y) - y_fit) / gv.sdev(fit.y)
    else:
        res = {}
        for key, val in y_fit.items():
            res[key] = (gv.mean(fit.y[key]) - val) / gv.sdev(fit.y[key])

    return res


def plot_errors(fig, x, y, err, name="Data", **kwargs):
    if not isinstance(x, (list, np.ndarray)):
        x = np.arange(len(y))
    fig.add_trace(
        go.Scatter(
            x=x, y=y, error_y={"type": "data", "array": err}, name=name, mode="markers",
        ),
        **kwargs,
    )


def plot_band(fig, x, y_min, y_mean, y_max, name="Fit", **kwargs):
    if not isinstance(x, (list, np.ndarray)):
        x = np.arange(len(y_mean))
    fig.add_trace(
        go.Scatter(
            x=list(x) + list(x)[::-1],
            y=list(y_max) + list(y_min)[::-1],
            fill="toself",
            mode="lines",
            line_color="indigo",
            name=name,
            opacity=0.8,
            legendgroup=name,
        ),
        **kwargs,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_mean,
            mode="lines",
            line_color="indigo",
            showlegend=False,
            legendgroup=name,
        ),
        **kwargs,
    )


def get_fit_fig(fit):

    x_fit, y_min_fit, y_mean_fit, y_max_fit = get_fit_bands(fit)
    residuals = get_residuals(fit)
    if not isinstance(fit.y, (dict, gv.BufferDict)):
        fig, r_fig = go.Figure(), go.Figure()
        plot_errors(fig, fit.x, gv.mean(fit.y), gv.sdev(fit.y))
        plot_band(fig, fit.x, y_min_fit, y_mean_fit, y_max_fit)
        plot_errors(fig, fit.x, gv.mean(residuals), gv.sdev(residuals))
    else:
        fig = make_subplots(cols=1, rows=len(fit.y), subplot_titles=list(fit.y.keys()))
        r_fig = make_subplots(
            cols=1, rows=len(fit.y), subplot_titles=list(fit.y.keys())
        )

        for n, (key, yy) in enumerate(fit.y.items()):
            xx = fit.x[key] if isinstance(fit.x, dict) else fit.x
            plot_errors(
                fig, xx, gv.mean(yy), gv.sdev(yy), name=f"{key} data", row=n + 1, col=1
            )
            plot_band(
                fig,
                xx,
                y_min_fit[key],
                y_mean_fit[key],
                y_max_fit[key],
                name=f"{key} fit",
                row=n + 1,
                col=1,
            )
            plot_errors(
                r_fig,
                xx,
                gv.mean(residuals[key]),
                gv.sdev(residuals[key]),
                name=key,
                row=n + 1,
                col=1,
            )

        fig.update_layout(height=len(fit.y) * 300)
        r_fig.update_layout(height=len(fit.y) * 300)
        r_fig.add_hline(0, line={"color": "black"})

    # residuals = get_residuals(fit)
    # data = DataFrame(
    #     data=np.transpose([fit.x, gv.mean(residuals), gv.sdev(residuals)]),
    #     columns=["x", "r", "r_err"],
    # )
    # r_fig = px.scatter(data, x="x", y="r", error_y="r_err")
    # r_fig.add_trace(
    #     go.Scatter(x=fit.x, y=np.zeros(len(fit.x)), mode="lines", line_color="black")
    # )

    fig.update_layout(
        template="plotly_white", font={"size": 16}, hoverlabel={"font_size": 16},
    )
    return fig, r_fig


COLORS = {"prior": "blue", "posterior": "green"}


def get_p2p_fig(fit):
    figs = {}
    for n, (key, prior) in enumerate(fit.prior.items()):
        posterior = fit.p[key]
        fig = go.Figure(layout_title=key,)

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
            )
        figs[key] = fig
    return figs


def init_dasboard(input_fit: nonlinear_fit):
    """Initializes dashboard from fit."""
    set_page_config(layout="wide")
    title("lsqfit-gui")
    try:
        expr = parse_fit_fcn(input_fit)
        with expander("Show fit function", expanded=False):
            header("Fit function")
            latex("f(x) = " + expr)
    except Exception:
        pass

    prior = sidebar_from_prior(input_fit.prior)
    fit = nonlinear_fit(input_fit.data, input_fit.fcn, prior)

    with expander("Show details", expanded=True):
        header("Fit details")
        code(fit.format(maxline=True), language=None)

    header("Plots")
    try:
        fig_fit, fig_residuals = get_fit_fig(fit)
        with expander("Show fit", expanded=True):
            subheader("Data vs fit")
            plotly_chart(fig_fit, use_container_width=True)

        with expander("Show residuals", expanded=False):
            subheader("Residuals")
            plotly_chart(fig_residuals, use_container_width=True)
    except Exception as error:
        warning(f"Failed to plot fit function:\n{error}")
        raise error

    header("Posteriors and priors")
    for key, fig in get_p2p_fig(fit).items():
        with expander(key, expanded=False):
            plotly_chart(fig, use_container_width=True)
