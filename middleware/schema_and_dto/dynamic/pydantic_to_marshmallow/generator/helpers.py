from typing import get_origin, Union, get_args


def is_optional(typ):
    return get_origin(typ) is Union and type(None) in get_args(typ)


def extract_inner_type(typ):
    if is_optional(typ):
        return next(t for t in get_args(typ) if t is not type(None))
    return typ
