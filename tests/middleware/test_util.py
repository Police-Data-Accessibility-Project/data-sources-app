import os
import pytest
from unittest.mock import patch
from middleware.util import get_env_variable

GET_ENV_PATH = "middleware.util.get_env_variable"
DOTENV_PATH = "middleware.util.dotenv_values"

@patch(GET_ENV_PATH)
@patch(DOTENV_PATH)
def test_get_env_variable_valid(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {"test_var": "test_value"}
    mock_os_getenv.return_value = "test_value"

    assert get_env_variable("test_var") == "test_value"


@patch(GET_ENV_PATH)
@patch(DOTENV_PATH)
def test_get_env_variable_not_set(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {}
    mock_os_getenv.return_value = None

    with pytest.raises(ValueError):
        get_env_variable("not_set_var")


@patch(GET_ENV_PATH)
@patch(DOTENV_PATH)
def test_get_env_variable_empty(mock_dotenv_values, mock_os_getenv):
    mock_dotenv_values.return_value = {"empty_var": ""}
    mock_os_getenv.return_value = ""

    with pytest.raises(ValueError):
        get_env_variable("empty_var")
