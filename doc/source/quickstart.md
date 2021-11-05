# Quick start

## Install

To install the package and its dependencies, run
```
pip install --upgrade numpy scipy
pip install [-e] .
```
_(`lsqfit` and `gvar` require `numpy` and `scipy` as build dependencies. Installing these packages before install `gvar` ensures a smooth installation.)_

## Usage

The GUI can be started either:

1. directly from another python script
```python
# some_script.py
from lsqfit import nonlinear_fit
from lsqfitgui import run_server
...
fit = nonlinear_fit(data, fcn=fcn, prior=prior)
run_server(fit)
```

2. or over the entry point, which requires a `gvar` pickled fit and an import path to the fit function.
As an example, first export the fit running the following script,
```python
#other_script.py
import gvar as gv
from lsqfit import nonlinear_fit

def fcn(x, p):
    y = ...
    return y

...

fit = nonlinear_fit(data, fcn=fcn, prior=prior)
gv.dump(fit, "fit.p")
```
and run the GUI with
```bash
lsqfitgui [--function other_script.py:fcn] fit.p
```

## Advanced usage
See also the [`examples/`](https://github.com/ckoerber/lsqfit-gui/tree/master/example) folder and [documentation](/examples).
