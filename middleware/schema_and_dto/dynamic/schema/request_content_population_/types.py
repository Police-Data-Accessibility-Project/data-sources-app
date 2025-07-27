from enum import Enum
from typing import TypeAlias, Union

JSONValue: TypeAlias = Union[
    str, int, float, bool, None, dict[str, "JSONValue"], list["JSONValue"]
]
JSONDict: TypeAlias = dict[str, JSONValue]

ValidatedValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
    Enum,
    dict[str, "ValidatedValue"],
    list["ValidatedValue"],
]
ValidatedDict: TypeAlias = dict[str, ValidatedValue]
