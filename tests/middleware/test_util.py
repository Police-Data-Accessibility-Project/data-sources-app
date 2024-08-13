import os
import pytest
from unittest.mock import patch, MagicMock
from middleware.util import get_env_variable
from tests.helper_scripts.DymamicMagicMock import DynamicMagicMock


class GetEnvVariableMocks(DynamicMagicMock):
    dotenv_values: MagicMock
    get_env_variable: MagicMock

@pytest.mark.parametrize(
    "dotenv_values, os_getenv, variable_name, expected_result, expected_exception",
    [
        (
            {"test_var": "test_value"},
            "test_value",
            "test_var",
            "test_value",
            None,
        ),  # Valid case
        ({}, None, "not_set_var", None, ValueError),  # Variable not set
        ({"empty_var": ""}, "", "empty_var", None, ValueError),  # Variable set to empty
    ],
)
def test_get_env_variable(
    dotenv_values,
    os_getenv,
    variable_name,
    expected_result,
    expected_exception,
):
    mock = GetEnvVariableMocks(
        patch_root="middleware.util",
        mocks_to_patch=["dotenv_values", "get_env_variable"],
        return_values={
            "get_env_variable": os_getenv,
            "dotenv_values": dotenv_values,
        },
    )

    if expected_exception:
        with pytest.raises(expected_exception):
            get_env_variable(variable_name)
    else:
        assert get_env_variable(variable_name) == expected_result
