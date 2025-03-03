from typing import Optional, Any

from utilities.argument_checking_logic import (
    MutuallyExclusiveArgumentError,
    MissingRequiredArgumentError,
)


def check_for_mutually_exclusive_arguments(arg1: Optional[Any], arg2: Optional[Any]):
    if arg1 is not None and arg2 is not None:
        raise MutuallyExclusiveArgumentError(arg1, arg2)


def check_for_either_or_argument(arg1: Optional[Any], arg2: Optional[Any]):
    if arg1 is None and arg2 is None:
        raise MissingRequiredArgumentError("source", "attribute_source_mapping")
