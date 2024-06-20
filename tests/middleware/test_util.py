import os
import pytest
from unittest.mock import patch
from middleware.util import get_env_variable


@patch("middleware.util.os.getenv")
@patch("middleware.util.dotenv_values")
def test_get_env_variable_valid(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {"test_var": "test_value"}
    mock_os_getenv.return_value = "test_value"

    assert get_env_variable("test_var") == "test_value"


@patch("middleware.util.os.getenv")
@patch("middleware.util.dotenv_values")
def test_get_env_variable_not_set(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {}
    mock_os_getenv.return_value = None

    with pytest.raises(ValueError):
        get_env_variable("not_set_var")


@patch("middleware.util.os.getenv")
@patch("middleware.util.dotenv_values")
def test_get_env_variable_empty(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {"empty_var": ""}
    mock_os_getenv.return_value = ""

    with pytest.raises(ValueError):
        get_env_variable("empty_var")
