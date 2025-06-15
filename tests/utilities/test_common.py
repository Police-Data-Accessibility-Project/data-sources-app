from enum import Enum
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from datetime import date

from werkzeug.exceptions import BadRequest

from utilities.common import (
    convert_dates_to_strings,
    get_enums_from_string,
    get_valid_enum_value,
)


def test_empty_dict():
    assert convert_dates_to_strings({}) == {}


def test_no_dates():
    assert convert_dates_to_strings({"key": "value"}) == {"key": "value"}


def test_single_date():
    input_dict = {"date": date(2022, 1, 1)}
    expected_dict = {"date": "2022-01-01"}
    assert convert_dates_to_strings(input_dict) == expected_dict


def test_multiple_dates():
    input_dict = {"date1": date(2022, 1, 1), "date2": date(2022, 2, 2)}
    expected_dict = {"date1": "2022-01-01", "date2": "2022-02-02"}
    assert convert_dates_to_strings(input_dict) == expected_dict


# Define a test enum class for testing purposes
class TestEnum(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


def test_get_enums_from_string_valid_input():
    input_string = "alpha, beta"
    expected_output = [TestEnum.ALPHA, TestEnum.BETA]
    assert get_enums_from_string(TestEnum, input_string) == expected_output


def test_get_enums_from_string_valid_input_with_whitespace():
    input_string = " alpha , beta "
    expected_output = [TestEnum.ALPHA, TestEnum.BETA]
    assert get_enums_from_string(TestEnum, input_string) == expected_output


def test_get_enums_from_string_valid_input_single_enum():
    input_string = "gamma"
    expected_output = [TestEnum.GAMMA]
    assert get_enums_from_string(TestEnum, input_string) == expected_output


def test_get_enums_from_string_invalid_input():
    input_string = "alpha, delta"
    with pytest.raises(ValueError) as excinfo:
        get_enums_from_string(TestEnum, input_string)
    assert "Invalid enum names: delta" in str(excinfo.value)


def test_get_enums_from_string_invalid_input_multiple():
    input_string = "delta, omega"
    with pytest.raises(ValueError) as excinfo:
        get_enums_from_string(TestEnum, input_string)
    assert "Invalid enum names: delta, omega" in str(excinfo.value)


def test_get_enums_from_string_empty_input():
    input_string = ""
    expected_output = None
    assert get_enums_from_string(TestEnum, input_string) == expected_output


def test_get_enums_from_string_all_valid_enum_members():
    input_string = "alpha, beta, gamma"
    expected_output = [TestEnum.ALPHA, TestEnum.BETA, TestEnum.GAMMA]
    assert get_enums_from_string(TestEnum, input_string) == expected_output


def test_get_enums_from_string_all_valid_case_insensitive():
    input_string = "ALPHA, beta, gAmMa"
    expected_output = [TestEnum.ALPHA, TestEnum.BETA, TestEnum.GAMMA]
    assert (
        get_enums_from_string(TestEnum, input_string, case_insensitive=True)
        == expected_output
    )


def test_get_enums_from_string_invalid_input_case_insensitive():
    input_string = "DELTA, oMeGa"
    with pytest.raises(ValueError) as excinfo:
        get_enums_from_string(TestEnum, input_string, case_insensitive=True)
    assert "Invalid enum names: delta, omega" in str(excinfo.value)


def test_valid_enum_value_success():
    assert get_valid_enum_value(TestEnum, "alpha") == TestEnum.ALPHA


def test_valid_enum_value_failure(monkeypatch):
    with pytest.raises(BadRequest):
        get_valid_enum_value(TestEnum, "delta")
