from datetime import datetime, date
from enum import Enum
from typing import Sequence

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, ENUM as pgEnum


def iter_with_special_cases(instance, special_cases=None):
    """Generates key-value pairs for an instance, applying special case handling."""
    if special_cases is None:
        special_cases = {}
    for key in instance.__dict__.copy():
        # Skip the _sa_instance_state key
        if key == "_sa_instance_state":
            continue

        # Handle keys with special cases defined in the special_cases dictionary
        if key in special_cases:
            mapped_key_value_pairs = special_cases[key](instance).copy()
            for mapped_key, mapped_value in mapped_key_value_pairs:
                if mapped_value is not None:
                    yield mapped_key, mapped_value
        else:
            # General case for other keys
            value = getattr(instance, key)
            if isinstance(value, datetime) or isinstance(value, date):
                value = str(value)  # Convert datetime to string if needed
            yield key, value


def get_iter_model_list_of_dict(instance, attr_name: str):
    return [
        (
            attr_name,
            (
                [item.to_dict() for item in getattr(instance, attr_name)]
                if getattr(instance, attr_name) is not None
                else None
            ),
        )
    ]


def make_get_iter_model_list_of_dict(attr_name):
    return lambda instance: get_iter_model_list_of_dict(instance, attr_name=attr_name)


def enum_list_column(enum: type[Enum], name: str) -> Column[Sequence[str | Enum]]:
    return Column(ARRAY(pgEnum(*[e.value for e in enum], name=name)))


def enum_column(
    enum: type[Enum], name: str, default: Enum | None = None
) -> Column[str | Enum]:
    if default is None:
        return Column(pgEnum(*[e.value for e in enum], name=name))
    else:
        return Column(
            pgEnum(*[e.value for e in enum], name=name), default=default.value
        )
