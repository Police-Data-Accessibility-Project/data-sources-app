from dataclasses import is_dataclass, asdict
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


def get_enum_values(en: type[Enum]) -> list[str]:
    return [e.value for e in en]


def dict_enums_to_values(d: dict[str, Any]) -> dict[str, Any]:
    """
    Convert enums within a dictionary to their values.
    """
    for key, value in d.items():
        if isinstance(value, Enum):
            d[key] = value.value
    return d


def dataclass_to_filtered_dict(instance: Any) -> Dict[str, Any]:
    """
    Convert a dataclass instance to a dictionary, filtering out any None values.
    :param instance:
    :return:
    """
    if is_dataclass(instance):
        d = asdict(instance)  # pyright: ignore[reportArgumentType]
    elif isinstance(instance, BaseModel):
        d = dict(instance)
    else:
        raise TypeError(
            f"Expected a dataclass or basemodel instance, but got {type(instance).__name__}"
        )
    results = {}
    for key, value in d.items():
        # Special case for Enum
        if isinstance(value, Enum):
            results[key] = value.value
        # Special case for List of Enum
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], Enum):
            results[key] = [e.value for e in value]
        elif value is not None:
            results[key] = value
    return results


def stringify_list_of_ints(l: list[int]) -> list[str]:
    new_list = []
    for i in range(len(l)):
        new_list.append(str(l[i]))
    return new_list


def stringify_lists(d: dict):
    for k, v in d.items():
        if isinstance(v, dict):
            stringify_lists(v)
        if isinstance(v, list):
            v = stringify_list_of_ints(v)
            d[k] = ",".join(v)
    return d
