from typing import Callable, Any

from marshmallow import Schema
from pydantic import BaseModel

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.core import \
    _get_source_getting_function
from middleware.schema_and_dto.exceptions import AttributeNotInClassError
from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters
from middleware.util.argument_checking import (
    check_for_mutually_exclusive_arguments,
    check_for_either_or_argument,
)
from utilities.enums import SourceMappingEnum


def populate_dto_with_request_content(
    populate_parameters: DTOPopulateParameters,
) -> BaseModel:
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
    dto_class = populate_parameters.dto_class
    transformation_functions = populate_parameters.transformation_functions
    source = populate_parameters.source
    attribute_source_mapping = populate_parameters.attribute_source_mapping
    validation_schema = populate_parameters.validation_schema

    # Instantiate object
    check_for_mutually_exclusive_arguments(source, attribute_source_mapping)
    check_for_either_or_argument(source, attribute_source_mapping)

    values = _get_values(dto_class, source)
    _optionally_check_against_schema(validation_schema, values)

    instantiated_object = dto_class(**values)
    _apply_transformation_functions(instantiated_object, transformation_functions)

    return instantiated_object


def _optionally_check_against_schema(
    validation_schema: Schema | None,
    values: dict[str, Any]
):
    if validation_schema is not None:
        validation_schema().load(values)


def _get_values(dto_class, source):
    # TODO: Are both logic branches used?
    values = _get_class_attribute_values_from_request(dto_class, source)

    return values


def _apply_transformation_functions(
    instantiated_object: BaseModel,
    transformation_functions: dict[str, Callable] | None = None,
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
    object_class: type[BaseModel],
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
