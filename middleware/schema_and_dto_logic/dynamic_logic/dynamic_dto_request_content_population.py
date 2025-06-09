from typing import Type, Optional, Callable, Any

from middleware.util.argument_checking import (
    check_for_mutually_exclusive_arguments,
    check_for_either_or_argument,
)
from middleware.schema_and_dto_logic.exceptions import AttributeNotInClassError
from middleware.schema_and_dto_logic.types import DTOTypes, ValidationSchema
from middleware.schema_and_dto_logic.util import _get_source_getting_function
from utilities.enums import SourceMappingEnum


def populate_dto_with_request_content(
    dto_class: Type[DTOTypes],
    transformation_functions: Optional[dict[str, Callable]] = None,
    source: SourceMappingEnum = None,
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None,
    validation_schema: Optional[ValidationSchema] = None,
) -> DTOTypes:
    """
    Populate dto with data from the request
    Will call `request.args.get` for each attribute
    Optionally applies transformation functions to select specific attributes
    :object_class: The class to instantiate and populate with data from the request
    :source: Mutually exclusive with source_attribute_mapping; used to designate the getter for all request attributes
    :source_attribute_mapping: Mutually exclusive with source; used to map specific attributes to different request getters
    :transformation_functions: A dictionary whose key-value pairs are the attributes to apply a transformation function to, and the transformation function
    :validation_schema: A schema used to validate the input is in the expected form.
    :return: The instantiated object populated with data from the request
    """
    # Instantiate object
    check_for_mutually_exclusive_arguments(source, attribute_source_mapping)
    check_for_either_or_argument(source, attribute_source_mapping)

    values = _get_values(attribute_source_mapping, dto_class, source)
    _optionally_check_against_schema(validation_schema, values)

    instantiated_object = dto_class(**values)
    _apply_transformation_functions(instantiated_object, transformation_functions)

    return instantiated_object


def _optionally_check_against_schema(validation_schema, values):
    if validation_schema is not None:
        validation_schema().load(values)


def _get_values(attribute_source_mapping, dto_class, source):
    if source is not None:
        values = _get_class_attribute_values_from_request(dto_class, source)
    elif attribute_source_mapping is not None:
        values = _get_class_attribute_values_from_request_source_mapping(
            dto_class, attribute_source_mapping
        )
    return values


def _apply_transformation_functions(
    instantiated_object: DTOTypes,
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


def _get_class_attribute_values_from_request(
    object_class: Type[DTOTypes],
    source: SourceMappingEnum = SourceMappingEnum.QUERY_ARGS,
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
    object_class: Type[DTOTypes], source_mapping: dict[str, SourceMappingEnum]
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
