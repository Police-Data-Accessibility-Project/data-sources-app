class MutuallyExclusiveArgumentError(ValueError):
    """Raised when mutually exclusive arguments are passed to a function."""

    def __init__(self, arg1, arg2):
        super().__init__(f"Arguments '{arg1}' and '{arg2}' cannot be used together.")


class MissingRequiredArgumentError(ValueError):
    """Raised when neither of the required mutually exclusive arguments are passed to a function."""

    def __init__(self, arg1, arg2):
        super().__init__(f"One of '{arg1}' or '{arg2}' must be provided.")
