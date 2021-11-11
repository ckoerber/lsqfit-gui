"""Provide consistent API for callbacks."""
from typing import Optional, Tuple, Dict, Any, Callable, Union


class CallbackWrapper:
    """Class which provides a call method and args and kwargs attribute."""

    def __init__(
        self,
        fcn: Callable,
        args: Optional[Union[Tuple[Any, Any, Any], Tuple[Any, Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize callback with method and args, kwargs."""
        self._fcn = fcn
        self.args = args or ()
        self.kwargs = kwargs or {"prevent_initial_call": True}

    def __call__(self, *args, **kwargs):
        """Wraps fcn."""
        return self._fcn(*args, **kwargs)
