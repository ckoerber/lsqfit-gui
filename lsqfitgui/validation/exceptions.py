"""Custom exceptions for lsqfitgui."""


class SetupException(Exception):
    """Exceptions associated with incorrectly setting up the GUI."""

    def __init__(self, exceptions):
        """Create exception which stores sub exceptions."""
        super().__init__("Encountered errors when setting up the GUI.\n")
        self.exceptions = exceptions

    def __str__(self):
        """Print error message."""
        return super().__str__() + "\n".join(map(str, self.exceptions))
