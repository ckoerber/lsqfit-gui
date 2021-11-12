"""Submodule providing GUI content."""
from typing import Optional, Dict, Callable, List, Any

from inspect import getsource

from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from lsqfitgui.plot.fit import plot_fit, plot_residuals, RESIDUALS_DESCRIPTION
from lsqfitgui.plot.uncertainty import plot_gvar
from lsqfitgui.util.function import parse_function_expression
from lsqfitgui.util.versions import get_entrypoint_string, get_version_string
from lsqfitgui.util.callback import CallbackWrapper


def document_function(
    fcn: Callable,
    parameters: Optional[Dict] = None,
    x_dict_keys: Optional[List[str]] = None,
    tex_function: bool = True,
) -> List[html.Base]:
    """Documents the function."""
    documentation = []
    if fcn is None:
        return None

    fcn_name = (
        fcn.__qualname__
        if hasattr(fcn, "__qualname__") and fcn.__qualname__
        else (fcn.__name__ if hasattr(fcn, "__name__") and fcn.__name__ else None)
    )
    if fcn_name:
        fcn_string = "```python\n"
        fcn_string += (
            f"from {fcn.__module__} import "
            if hasattr(fcn, "__module__") and fcn.__module__
            else ""
        )
        fcn_string += fcn_name + "\n```"
        documentation.append(dcc.Markdown(fcn_string))

    documentation.append(
        html.Pre(get_entrypoint_string() + "\n" + get_version_string())
    )

    if parameters and tex_function:
        tex = parse_function_expression(fcn, parameters, x_dict_keys=x_dict_keys)
        if tex:
            documentation.append(html.P(fr"$${tex}$$"))

    if hasattr(fcn, "__doc__") and fcn.__doc__:
        documentation.append(html.Pre(html.Code(fcn.__doc__)))

    try:
        source = getsource(fcn)
    except Exception:
        source = "Unable to load source"
    finally:
        documentation.append(
            html.Div(
                [
                    html.Button(
                        "Show source code",
                        className="btn btn-outline-primary btn-small",
                        id="collapse-function-source-button",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Markdown(f"```python\n{source}\n```"),
                                className="p-4",
                            ),
                        ),
                        id="collapse-function-source",
                        is_open=False,
                    ),
                ],
                className="py-4",
            )
        )

    return documentation


def _toggle_function_source_collapse(n, is_open):
    """Toggles the source code of the function."""
    return not is_open if n else is_open


FCN_SOURCE_CALLBACK = CallbackWrapper(
    _toggle_function_source_collapse,
    args=(
        Output("collapse-function-source", "is_open"),
        [Input("collapse-function-source-button", "n_clicks")],
        [State("collapse-function-source", "is_open")],
    ),
)


DEFAULT_PLOTS: List[Dict[str, Any]] = [
    {"name": "Fit", "fcn": plot_fit},
    {"name": "Residuals", "fcn": plot_residuals, "description": RESIDUALS_DESCRIPTION},
]
"""Plots which are added to the GUI by default."""


def get_figures(fit, plots: Optional[List[Dict[str, Any]]] = None):
    """Infers the figures to be plotted from the most recent fit and plot config."""
    plots = plots or []
    figure_data = []
    for n, data in enumerate(plots):
        kwargs = data.get("kwargs", {})
        fcn = data.get("fcn")
        static_data = data.get("static_plot_gvar", {})

        fig = None
        if fcn is not None:
            fig = fcn(fit, **kwargs)
        if static_data:
            fig = plot_gvar(**static_data, fig=fig)
        if fig is None:
            raise ValueError(f"Could not infer figure from {data}")

        figure_data.append(
            {
                "label": data.get("name", f"Figure {n}"),
                "tab-value": f"figure-{n}",
                "figure": fig,
                "description": data.get("description"),
            }
        )
    return figure_data
