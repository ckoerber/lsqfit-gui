"""The Python package **lsqfitgui** provides a Graphical User Interface to ``lsqfit``.

The :class:`FitGUI` class provides the interface to ``lsqfit`` providing dynamic html elements which can be embedded into a ``dash`` (``flask``) app.
The :func:`run_server` method provides a convinient interafce creating the GUI and starting the dash which is accessible by any (local) browser.

The :func:`wrap_plot_gvar` and :func:`plot_gvar` methods can be used to generate plots form gvars.
"""  # noqa: E501
from lsqfitgui.lsqfitgui import FitGUI, run_server  # noqa
from lsqfitgui.plot.uncertainty import wrap_plot_gvar, plot_gvar  # noqa
from lsqfitgui.frontend.body import (  # noqa
    BodyTemplate,
    DefaultBodyTemplate,
    DEFAULT_PLOTS,
)
from lsqfitgui.version import __version__  # noqa

__all__ = [
    "FitGUI",
    "run_server",
    "wrap_plot_gvar",
    "plot_gvar",
    "BodyTemplate",
    "DefaultBodyTemplate",
    "DEFAULT_PLOTS",
    "__version__",
]
