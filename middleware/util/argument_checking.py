from typing import Optional, Any

from utilities.argument_checking_logic import (
    MutuallyExclusiveArgumentError,
    MissingRequiredArgumentError,
)


def check_for_mutually_exclusive_arguments(arg1: Any, arg2: Any):
    if arg1 is not None and arg2 is not None:
        raise MutuallyExclusiveArgumentError(arg1, arg2)

