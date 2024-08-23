"""
This module aims to reduce the amount of boilerplate code
with retrieving requests and populating Data Transfer Objects (DTO)s
By dynamically populating an DTO with data from the request,
    based on the attributes defined in the DTO
"""
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, Type

from flask import request
from enum import Enum

T = TypeVar("T")


class SourceMappingEnum(Enum):
    ARGS = "args"
    FORM = "form"
    JSON = "json"

@dataclass
class DTOPopulateParameters:
    dto_class: Type[T]
    source: Optional[SourceMappingEnum] = None
    transformation_functions: Optional[dict[str, Callable]] = None
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None


def populate_dto_with_request_content(
    dto_class: Type[T],
    transformation_functions: Optional[dict[str, Callable]] = None,
    source: SourceMappingEnum = None,
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None,
) -> T:
    """
    Populate dto with data from the request
    Will call `request.args.get` for each attribute
    Optionally applies transformation functions to select specific attributes
    :object_class: The class to instantiate and populate with data from the request
    :source: Mutually exclusive with source_attribute_mapping; used to designate the getter for all request attributes
    :source_attribute_mapping: Mutually exclusive with source; used to map specific attributes to different request getters
    :transformation_functions: A dictionary whose key-value pairs are the attributes to apply a transformation function to, and the transformation function
    :return: The instantiated object populated with data from the request
    """
    # Instantiate object
    if source is not None and attribute_source_mapping is not None:
        raise MutuallyExclusiveArgumentError("source", "attribute_source_mapping")
    if source is not None:
        values = _get_class_attribute_values_from_request(dto_class, source)
    elif attribute_source_mapping is not None:
        values = _get_class_attribute_values_from_request_source_mapping(
            dto_class, attribute_source_mapping
        )
    else:
        raise MissingRequiredArgumentError("source", "attribute_source_mapping")

    instantiated_object = dto_class(**values)
    _apply_transformation_functions(instantiated_object, transformation_functions)

    return instantiated_object


class AttributeNotInClassError(Exception):

    def __init__(self, attribute: str, class_name: str):
        super().__init__(
            f"The attribute '{attribute}' is not part of the class '{class_name}'"
        )


class MutuallyExclusiveArgumentError(ValueError):
    """Raised when mutually exclusive arguments are passed to a function."""

    def __init__(self, arg1, arg2):
        super().__init__(f"Arguments '{arg1}' and '{arg2}' cannot be used together.")


class MissingRequiredArgumentError(ValueError):
    """Raised when neither of the required mutually exclusive arguments are passed to a function."""

    def __init__(self, arg1, arg2):
        super().__init__(f"One of '{arg1}' or '{arg2}' must be provided.")


def _apply_transformation_functions(
    instantiated_object: T,
    transformation_functions: Optional[dict[str, Callable]] = None,
) -> None:
    """
    Apply transformation functions to select specific attributes
    Throws error when a transformation function is applied to an attribute not defined in the class
    :param instantiated_object: The instantiated object to apply the transformation function to
    :param transformation_functions: A dictionary whose key-value pairs are the attributes to apply a transformation function to, and the transformation function
    :return: None; modifies the instantiated object in place
    """
    if transformation_functions is None:
        return
    for attribute, transform in transformation_functions.items():
        try:
            value = getattr(instantiated_object, attribute)
        except AttributeError:
            raise AttributeNotInClassError(
                attribute, instantiated_object.__class__.__name__
            )
        if value is not None and callable(transform):
            value = transform(value)
        setattr(instantiated_object, attribute, value)


def _get_source_getting_function(source: SourceMappingEnum) -> Callable:
    source_mapping: dict[SourceMappingEnum, Callable] = {
        SourceMappingEnum.ARGS: request.args.get,
        SourceMappingEnum.FORM: request.form.get,
        SourceMappingEnum.JSON: lambda key: (
            request.json.get(key) if request.json else None
        ),
    }
    return source_mapping[source]


def _get_class_attribute_values_from_request(
    object_class: Type[T], source: SourceMappingEnum = SourceMappingEnum.ARGS
) -> dict[str, Any]:
    """
    Apply getter on all defined class attributes, returning a list of values
    :param object_class: The class whose attributes will be retrieved
    :param source: The source of the request
    :return: A list of values, in the order in which the attributes were defined in the class
    """
    values = {}
    getter = _get_source_getting_function(source)
    for attribute in object_class.__annotations__:
        values[attribute] = getter(attribute)
    return values


def _get_class_attribute_values_from_request_source_mapping(
    object_class: Type[T], source_mapping: dict[str, SourceMappingEnum]
) -> dict[str, Any]:
    """
    Apply multiple getters on all defined class attributes,
        according to the source mapping, returning a dictionary of values
    :param object_class: The class whose attributes will be retrieved
    :return: A list of values, in the order in which the attributes were defined in the class
    """
    values = {}
    for attribute, source in source_mapping.items():
        if attribute not in object_class.__annotations__:
            raise AttributeNotInClassError(attribute, object_class.__name__)
        getter = _get_source_getting_function(source)
        values[attribute] = getter(attribute)
    return values
