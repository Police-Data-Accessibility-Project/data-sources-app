import ast
from dataclasses import dataclass
from http import HTTPStatus
from typing import Type, Optional

import marshmallow

from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.custom_types import SchemaTypes, DTOTypes
from middleware.schema_and_dto_logic.util import (
    _get_required_argument,
    _get_source_getting_function,
)
from utilities.enums import SourceMappingEnum


@dataclass
class NestedDTOInfo:
    key: str
    class_: Type


@dataclass
class SourceDataInfo:
    data: dict
    nested_dto_info_list: list[NestedDTOInfo]


def populate_schema_with_request_content(
    schema: SchemaTypes, dto_class: Type[DTOTypes]
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
    fields = schema.fields
    source_data_info = _get_data_from_sources(fields, schema)

    intermediate_data = validate_data(source_data_info.data, schema)

    _apply_transformation_functions_to_dict(fields, intermediate_data)

    return setup_dto_class(
        intermediate_data, dto_class, source_data_info.nested_dto_info_list
    )


def setup_dto_class(
    data: dict, dto_class: Type[DTOTypes], nested_dto_info_list: list[NestedDTOInfo]
):
    for nested_dto_info in nested_dto_info_list:
        if nested_dto_info.key in data:
            nested_dto = nested_dto_info.class_(**data[nested_dto_info.key])
            data[nested_dto_info.key] = nested_dto
        else:
            data[nested_dto_info.key] = None
    return dto_class(**data)


def validate_data(data, schema_obj):
    try:
        intermediate_data = schema_obj.load(data)
    except Exception as e:
        FlaskResponseManager.abort(code=HTTPStatus.BAD_REQUEST, message=str(e))
    return intermediate_data


class InvalidSourceMappingError(Exception):
    pass


def _get_data_from_sources(fields: dict, schema: SchemaTypes) -> SourceDataInfo:
    """
    Get data from sources specified in the schema and field metadata
    :param fields:
    :param schema:
    :return:
    """
    data = {}
    nested_dto_info_list = []
    for field_name, field_value in fields.items():
        metadata = field_value.metadata
        source: SourceMappingEnum = _get_required_argument("source", metadata, schema)
        if isinstance(field_value, marshmallow.fields.Nested):
            if source != SourceMappingEnum.JSON:
                raise InvalidSourceMappingError(
                    "Nested fields can only be populated from JSON sources"
                )
            if "nested_dto_class" not in metadata:
                raise InvalidSourceMappingError(
                    "Nested fields must have a 'nested_dto_class' metadata"
                )
            nested_dto_class = metadata["nested_dto_class"]
            nested_dto_info_list.append(
                NestedDTOInfo(key=field_name, class_=nested_dto_class)
            )

        source_getting_function = _get_source_getting_function(source)
        val = source_getting_function(field_name)
        if val is not None:
            data[field_name] = val
    return SourceDataInfo(data=data, nested_dto_info_list=nested_dto_info_list)


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
