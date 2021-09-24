# Lsqfit GUI

Graphical user interface for `lsqfit` using `dash`.

## Install

Run
```
pip install [-e] .
```

## Usage

Either directly use a fit object to spawn a server
```python
# some_script.py
from lsqfit import nonlinear_fit
from lsqfitgui import run_server
...
fit = nonlinear_fit(data, fcn=fcn, prior=prior)
run_server(fit)
```
or use the console script entry point pointing to a `gvar` pickeled fit (and a fit function)
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
and run
```bash
lsqfitgui [--function other_script.py:fcn] fit.p
```

Both commands will spawn a local serve to interface.

See also the `example` directory for more details.
