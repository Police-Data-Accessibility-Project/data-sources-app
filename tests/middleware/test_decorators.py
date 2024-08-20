from unittest.mock import MagicMock

import pytest
from flask_restx._http import HTTPStatus
from pytest_mock import mocker

from middleware.decorators import (
    api_key_required,
    permissions_required,
    check_decorator_factory,
)
from middleware.enums import PermissionsEnum


def test_decorator_factory():
    # Create a mock check function
    mock_check_func = MagicMock()

    sample_decorator = check_decorator_factory(mock_check_func)

    # Create a simple function to decorate
    # @check_decorator_factory(mock_check_func, "arg1", key="value")
    @sample_decorator
    def sample_function():
        return "Function Executed"

    # Call the decorated function
    result = sample_function()

    # Assert that the check function was called with the correct arguments
    # mock_check_func.assert_called_once_with("arg1", key="value")
    mock_check_func.assert_called_once()

    # Assert that the decorated function returns the correct value
    assert result == "Function Executed"

def test_decorator_factory_with_args_in_check_function():
    # Create a mock check function
    mock_check_func = MagicMock()

    sample_decorator = check_decorator_factory(mock_check_func, "arg1", key="value")

    # Create a simple function to decorate
    @sample_decorator
    def sample_function():
        return "Function Executed"

    # Call the decorated function
    result = sample_function()

    # Assert that the check function was called with the correct arguments
    mock_check_func.assert_called_once_with("arg1", key="value")

    # Assert that the decorated function returns the correct value
    assert result == "Function Executed"

def test_decorator_factory_with_args_in_decorator():
    # Create a mock check function
    mock_check_func = MagicMock()
    mock_decorator_parameter = MagicMock()

    sample_decorator = lambda dp: check_decorator_factory(mock_check_func, dp)

    # Create a simple function to decorate
    @sample_decorator(mock_decorator_parameter)
    def sample_function():
        return "Function Executed"

    # Call the decorated function
    result = sample_function()

    # Assert that the check function was called with the correct arguments
    mock_check_func.assert_called_once_with(mock_decorator_parameter)

    # Assert that the decorated function returns the correct value
    assert result == "Function Executed"
