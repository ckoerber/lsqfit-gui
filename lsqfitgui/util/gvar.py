"""Utility methods with gvars."""
from typing import Dict

from numpy import concatenate
from gvar import BufferDict, GVar


def flatten_gvars(gvars: BufferDict, flat_label: str = "__array_") -> Dict[str, GVar]:
    """Turn a BufferDict of gvars (possibly arrays) into a flat dict of gvars (numbers).

    Arguemnts:
        gvars: The BufferDict.
        flat_label: If keys are arrays, this label will be used in the flattened output.
    """
    keys = concatenate(
        [
            [f"{key}{flat_label}{n}" for n in range(len(val))]
            if hasattr(val, "__len__")
            else [key]
            for key, val in gvars.items()
        ]
    )
    vals = gvars.flatten()
    return dict(zip(keys, vals))
