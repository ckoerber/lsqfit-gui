"""Initializes dashboard from fit."""
from lsqfit import nonlinear_fit
from gvar import BufferDict, gvar
from gvar._gvarcore import GVar
from streamlit import sidebar, title, text


def add_gvar_widget(parent, name: str, gv: GVar):
    """Adds widget to parent for given gvar."""
    m, s = gv.mean, gv.sdev
    parent.label(name)
    mean = parent.number_input(label="mean", value=m, step=s / 3, key=f"{name}_mean")
    sdev = parent.text_input(label="sdev", value=s, step=s / 3, key=f"{name}_sdev")
    return mean, sdev


def sidebar_from_prior(prior: BufferDict) -> BufferDict:
    """Creates streamlit sidebar from prior."""
    pprior = BufferDict()
    for key, value in prior.items():
        if hasattr(value, "__iter__"):
            raise NotImplementedError("Prior array values not supported yet.")
        pprior[key] = gvar(add_gvar_widget(sidebar, key, value))
    return pprior


def init_dasboard(fit: nonlinear_fit):
    """Initializes dashboard from fit."""
    title("lsqfit-gui")

    prior = sidebar_from_prior(fit.prior)
    fit = nonlinear_fit(fit.data, fit.fcn, prior)
    text(fit.format(maxline=True))
