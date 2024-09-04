from http import HTTPStatus
from typing import Type

from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.custom_types import SchemaTypes, DTOTypes
from middleware.schema_and_dto_logic.util import _get_required_argument, _get_source_getting_function
from utilities.enums import SourceMappingEnum


def populate_schema_with_request_content(
    schema_class: Type[SchemaTypes], dto_class: Type[DTOTypes]
) -> DTOTypes:
    """
    Populates a marshmallow schema with request content, given custom arguments in the schema fields
    Custom arguments include:
    * source: The source in the request the data will be pulled from
    * transformation_function (optional): A function that will be applied to the data
    :param schema_class:
    :param dto_class:
    :return:
    """
    # Get all declared fields from the schema
    schema_obj = schema_class()
    fields = schema_obj.fields
    data = _get_data_from_sources(fields, schema_class)

    intermediate_data = validate_data(data, schema_obj)
    _apply_transformation_functions_to_dict(fields, intermediate_data)

    return dto_class(**intermediate_data)


def validate_data(data, schema_obj):
    try:
        intermediate_data = schema_obj.load(data)
    except Exception as e:
        FlaskResponseManager.abort(code=HTTPStatus.BAD_REQUEST, message=str(e))
    return intermediate_data


def _get_data_from_sources(fields, schema_class):
    """
    Get data from sources specified in the schema and field metadata
    :param fields:
    :param schema_class:
    :return:
    """
    data = {}
    for field_name, field_value in fields.items():
        metadata = field_value.metadata
        source: SourceMappingEnum = _get_required_argument(
            "source", metadata, schema_class
        )
        source_getting_function = _get_source_getting_function(source)
        val = source_getting_function(field_name)
        if val is not None:
            data[field_name] = val
    return data


def _apply_transformation_functions_to_dict(fields: dict, intermediate_data: dict):
    """
    Apply transformation functions to the data,
    based on the transformation functions, if any, located within the metadata
    :param fields:
    :param intermediate_data:
    :return:
    """
    for field_name, field_value in fields.items():

        # if transformation functions, apply them
        metadata = field_value.metadata
        transformation_function: callable = metadata.get(
            "transformation_function", None
        )
        if transformation_function is not None and field_name in intermediate_data:
            intermediate_data[field_name] = transformation_function(
                intermediate_data[field_name]
            )
