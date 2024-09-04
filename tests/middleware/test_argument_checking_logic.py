from typing import Any, Optional

import pytest

from middleware.argument_checking_logic import check_for_mutually_exclusive_arguments, check_for_either_or_argument
from utilities.argument_checking_logic import MutuallyExclusiveArgumentError, MissingRequiredArgumentError


@pytest.mark.parametrize(
    "arg1, arg2, raises_exception",
    (
        (None, None, False),
        ("arg1", None, False),
        (None, "arg2", False),
        ("arg1", "arg2", True),
    )
)
def test_check_for_mutually_exclusive_arguments(
    arg1: Optional[Any], arg2: Optional[Any], raises_exception: bool
):
    if raises_exception:
        with pytest.raises(MutuallyExclusiveArgumentError):
            check_for_mutually_exclusive_arguments(arg1, arg2)
    else:
        check_for_mutually_exclusive_arguments(arg1, arg2)

@pytest.mark.parametrize(
    "arg1, arg2, raises_exception",
    (
        (None, None, True),
        ("arg1", None, False),
        (None, "arg2", False),
        ("arg1", "arg2", False),
    )
)
def test_check_for_either_or_argument(
    arg1: Optional[Any], arg2: Optional[Any], raises_exception: bool
):
    if raises_exception:
        with pytest.raises(MissingRequiredArgumentError):
            check_for_either_or_argument(arg1, arg2)
    else:
        check_for_either_or_argument(arg1, arg2)