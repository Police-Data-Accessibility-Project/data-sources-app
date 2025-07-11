import datetime
from typing import get_origin

from marshmallow import fields

TYPE_MAPPING = {
    str: fields.String,
    int: fields.Integer,
    bool: fields.Boolean,
    float: fields.Float,
    datetime.date: fields.Date,
    datetime.datetime: fields.DateTime,
    dict: fields.Dict,
}


def _is_mapped_type(inner_type: type) -> bool:
    available_types = list(TYPE_MAPPING.keys())
    if get_origin(inner_type) in available_types:
        return True
    if inner_type in available_types:
        return True
    return False