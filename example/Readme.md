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

2. ... To be updated...
