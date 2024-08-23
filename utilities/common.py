import datetime
import re
import json
from enum import Enum
from http import HTTPStatus
from typing import Type, Union

from flask_restx import abort


def convert_dates_to_strings(data_dict: dict) -> dict:
    for key, value in data_dict.items():
        if key == "last_cached" and value is not None:
            data_dict[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, datetime.date):
            data_dict[key] = value.strftime("%Y-%m-%d")
    return data_dict


def format_arrays(data_dict):
    for key, value in data_dict.items():
        if value is not None and type(value) is str:
            if re.search(r"\"?\[ ?\".*\"\ ?]\"?", value, re.DOTALL):
                data_dict[key] = json.loads(value.strip('"'))
    return data_dict


def get_enums_from_string(
    enum_class: Type[Enum], comma_delimited_string: str, case_insensitive: bool = False
) -> Union[list[Enum], None]:
    # Split the input string into a list of names
    if len(comma_delimited_string) == 0:
        return None

    names = comma_delimited_string.split(",")

    # Strip any leading or trailing whitespace from the names
    names = [name.strip() for name in names]

    enum_values = [member.value for member in enum_class.__members__.values()]

    if case_insensitive:
        names = [name.lower() for name in names]
        enum_values = [name.lower() for name in enum_values]

    # Check for invalid names and raise an error if any are found
    invalid_names = [name for name in names if name not in enum_values]
    if invalid_names:
        raise ValueError(f"Invalid enum names: {', '.join(invalid_names)}")

    # Create a list of enums from the valid names
    result = [match_string_to_enum(name, enum_class) for name in names]

    return result


def match_string_to_enum(value: str, enum_class: Type[Enum]) -> Enum:
    # Convert input string to lowercase
    value_lower = value.lower()

    # Iterate through enum members and compare
    for member in enum_class:
        if member.value.lower() == value_lower:
            return member

    raise ValueError(
        f"'{value}' does not match any enum value in {enum_class.__name__}"
    )


def get_valid_enum_value(enum_type: Type[Enum], value: str) -> Enum:
    """
    Returns the appropriate enum value if it is valid, otherwise aborts the request.
    Must be within a Flask context
    :param enum_type:
    :param value:
    :return:
    """
    try:
        return match_string_to_enum(value, enum_type)
    except ValueError:
        abort(
            code=HTTPStatus.BAD_REQUEST,
            message=f"Invalid {enum_type.__name__} '{value}'. Must be one of the following: {[item.value for item in enum_type]}",
        )
