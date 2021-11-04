# Examples

<div class="admonition tip">
<p class="admonition-title">Tip</p>

In the `examples/` directory, we provide different examples which can be started by running

```bash
python example/{script}.py
```

and visiting <http://localhost:8000>.

</div>

## First steps

### Launching the dashboard via script

In the most simple case, `lsqfitgui` requires a [`lsqfit.nonlinear_fit` object](https://lsqfit.readthedocs.io/en/latest/lsqfit.html#nonlinear-fit-objects) as its only argument.

An example script capable of launching the GUI for a simple quadratic fit model is given by
```python
#my_fit.py
import numpy as np

from lsqfit import nonlinear_fit
from gvar import gvar

from lsqfitgui import run_server

x = np.linspace(0, 1, 10)
# first argument is the mean, second the standard deviation
y = gvar(x**2, np.ones(len(x)) * 0.1)

def fcn(x, p):
    return p["a0"] + p["a1"] * x + p["a2"] * x ** 2

prior = {"a0": gvar(0, 2), "a1": gvar(0, 2), "a2": gvar(0, 2)}

fit = nonlinear_fit(data=(x, y), fcn=fcn, prior=prior)

run_server(fit)
```
Running `python my_fit.py` launches the dashboard locally at <http://localhost:8000>.

This GUI allows for varying prior parameters (mean and standard deviations) and inspecting their effects on the fit.

### Launching the dashboard via CLI

Additionally, for a dumped fit object
```python
from gvar import dump

...
dump(fit, outputfile="fit.p")
```
it is possible to launch the GUI by running
```bash
lsqfitgui --function my_fit.py:fcn fit.p
```

## Meta parameters

For some fits, you may not only want to vary the prior parameters but also entirely change the model (or data).
This is done by the providing a `fit_setup_function` and respective configuration to the {func}`lsqfitgui.run_server` method.

```python
#my_fit.py
import numpy as np

from lsqfit import nonlinear_fit
from gvar import gvar

from lsqfitgui import run_server

x = np.linspace(0, 1, 10)
y = gvar(x**2, np.ones(len(x)) * 0.1)

# Modify the fit function to be flexible in the number of parameters
def fcn(x, p):
    return sum([p[f"a{n}"] * x **n for n in range(len(p))])

def generate_fit(n_order=2):
    prior = {f"a{n}": gvar(0, 2) for n in range(n_order+1)}
    return nonlinear_fit(data=(x, y), fcn=fcn, prior=prior)

run_server(fit_setup_function=generate_fit)
```

Running this script will launch the same dashboard as before.
To update the meta parameter `n_order` in the GUI, we have to provide an initial value
```python
fit_setup_kwargs = {"n_order": 2}
```
and parameters to set up a form
```python
meta_config = [{"name": "n_order", "type": "number", "min": 1, "max": 10, "step": 1}]
```
so that the actual run command is
```python
run_server(
    fit_setup_function=generate_fit,
    fit_setup_kwargs=fit_setup_kwargs,
    meta_config=meta_config
)
```

```{note}
You can provide more than just one meta setup parameter of arbitrary type.
These parameters can have any type allowed to be parsed from HTML widgets.
You can find more details about allowed ``meta_config`` parameters at the [``dcc.Input`` documentation](https://dash.plotly.com/dash-core-components/input#input-properties).
Note that the ``id`` of the widget is automatically provided by the ``name`` keyword from the ``meta_config`` dictionary, which must match the ``fit_setup_kwargs`` keyword and the ``generate_fit`` keyword.).
```


## Adding plots

If you want to add plots, you can use the ``additional_plots`` keyword.
The default options must provide a name and a function which takes a fit object and returns a [plotly.graph_objects.Figure](https://plotly.com/python/creating-and-updating-figures/#figures-as-graph-objects)
```python
from plotly.graph_objects import Figure

def plot_fcn(fit):
    fig = Figure()
    ...
    return fig

additional_plots = [{"name": "My plot", "fcn": plot_fcn}]
run_server(
    fit_setup_function=generate_fit,
    fit_setup_kwargs=fit_setup_kwargs,
    meta_config=meta_config,
    additional_plots=additional_plots,
)
```
This method adds plots to the already existing plots container.

For convenience, we have also added methods for creating figures directly from ``gvars``.
For example, if you want to add a custom function ``my_func`` to the plot, you can add the lines
```python
from lsqfitgui import plot_gvar

def my_func(x, p):
    yy = ...
    return yy

def plot_my_func(fit):
    y_fit = my_func(fit.x, fit.p)
    return plot_gvar(fit.x, y_fit, kind="errorband")

additional_plots = [{"name": "My function", "fcn": plot_log_log}]
```
Additionally, if you have a function that already takes `x` and `p` arguments as the fit function of the `nonlinear_fit` object, you can use
```python
from lsqfitgui import wrap_plot_gvar

@wrap_plot_gvar(kind="band")
def plot_my_func_wrapped(x, p):
    return my_func(x, p)

additional_plots = [{
    "name": "My function",
    "fcn": plot_my_func_wrapped,
    "description": "This figure displays my function.", # optional
}]
```
which does effectively the same thing.

### Additional kwargs

The ``additional_plots`` list also allows dictionaries with more keyword arguments.
Allowed are

* **name** *(str)*: The name presented in the tabs.
* **fcn** *(Callable[[nonlinear_fit], Figure])*: The function used to generate the plot. Must take a plot and kwargs as an input.
* **kwargs** *(Dict[str, Any])*: A dictionary passed to the provided function.
* **static_plot_gvar** *(Dict[str, Any])*: Static data passed to {func}`lsqfitgui.plot_gvar` added to the same figure (i.e., to also plot data as an comparison).

For example, one setup could be
```python
x_data, y_data = ... # some static values to compare against

additional_plots = [{
    "name": "My function",
    "fcn": plot_my_func_wrapped,
    "static_plot_gvar": {
        "x": x_data,
        "y": y_data,
        "kind": "errorbars",
        "scatter_kwargs": {"name": "Data"} # Is passed to go.Scatter
    }
}]
```


## Further usage

See also the [``example`` directory](https://github.com/ckoerber/lsqfit-gui/tree/master/example) or API docs.
