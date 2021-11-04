# lsqfitgui examples

1. Polynomial fit using a python script or the cli entrypoint (`fit.py` and `entrypoint.py`).

To export a pickled fit (`fit.p`), run
```bash
python fit.py
```
afterwards,
```bash
lsqfitgui [--function other_script.py:fcn] fit.p
```
starts the server.

Alternatively, you can run
```bash
python enrtypoint.py
```
to also use the `meta_config` version.

2. The `lsqfit` basic example for multi-exponential fits is described by `lsqfit_basic_example.py`

3. The `multi_key_example.py` example shows how arrays of priors can be used.

4. The `lsqfit_stability_example.py` provides a first draft for generating stability plots.
