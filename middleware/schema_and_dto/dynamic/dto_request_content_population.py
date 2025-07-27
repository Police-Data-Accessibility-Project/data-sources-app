from typing import Callable, Any

from marshmallow import Schema
from pydantic import BaseModel

from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.core import \
    get_data_from_source
from middleware.schema_and_dto.exceptions import AttributeNotInClassError
from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters


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
    pp = populate_parameters
    dto_class = pp.dto_class

    # Instantiate object

    values = get_data_from_source(
        source=pp.source,
        fields=list(dto_class.__annotations__.keys())
    )
    _optionally_check_against_schema(
        validation_schema=pp.validation_schema,
        values=values
    )

    instantiated_object = dto_class(**values)
    _apply_transformation_functions(
        instantiated_object=instantiated_object,
        transformation_functions=pp.transformation_functions
    )

    return instantiated_object


def _optionally_check_against_schema(
    validation_schema: Schema | None,
    values: dict[str, Any]
):
    if validation_schema is not None:
        validation_schema().load(values)

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

