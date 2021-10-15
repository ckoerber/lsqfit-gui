"""The Python package **lsqfitgui** provides a Graphical User Interface to `lsqfit`.

The object creating the GUI is the :class:`FitGUI` class.
The :func:`run_server` method provides a convinient interafce which also starts the Dash app.

The :func:`wrap_plot_gvar` and :func:`plot_gvar` methods can be used to generate plots form gvars.
"""  # noqa: E501
from lsqfitgui.lsqfitgui import FitGUI, run_server  # noqa
from lsqfitgui.plot.uncertainty import wrap_plot_gvar, plot_gvar  # noqa

__all__ = ["FitGUI", "run_server", "wrap_plot_gvar", "plot_gvar"]
