import pytest
from datetime import date
from utilities.common import convert_dates_to_strings


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
