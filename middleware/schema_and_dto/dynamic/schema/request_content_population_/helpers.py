from typing import Any

import marshmallow
from marshmallow import Schema
from pydantic import BaseModel
from werkzeug.exceptions import BadRequest

from middleware.schema_and_dto.dynamic.schema.request_content_population_.exceptions import (
    InvalidSourceMappingError,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.models.nested_dto import (
    NestedDTOInfo,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.models.source_data import (
    SourceDataInfo,
)
from middleware.schema_and_dto.dynamic.schema.request_content_population_.types import JSONDict, ValidatedDict

from middleware.schema_and_dto.dynamic.schema.request_content_population_.util import _get_required_argument
from middleware.schema_and_dto.dynamic.schema.request_content_population_.source_extraction.core import \
    _get_source_getting_function
from utilities.enums import SourceMappingEnum


def setup_dto_class(
    data: ValidatedDict,
    dto_class: type[BaseModel],
    nested_dto_info_list: list[NestedDTOInfo]
) -> BaseModel:
    """Setup DTO class based on data and nested DTO info list."""
    for nested_dto_info in nested_dto_info_list:
        if nested_dto_info.key in data:
            nested_dto = nested_dto_info.class_(**data[nested_dto_info.key])
            data[nested_dto_info.key] = nested_dto
        else:
            data[nested_dto_info.key] = None
    return dto_class(**data)


def validate_data(data: JSONDict, schema_obj: Schema) -> ValidatedDict:
    """Validate data against the schema and perform type coercions."""
    try:
        intermediate_data = schema_obj.load(data, unknown=marshmallow.RAISE)  # pyright: ignore [reportUnknownVariableType]
    except Exception as e:
        raise BadRequest(str(e))
    return intermediate_data  # pyright: ignore [reportUnknownVariableType]


def get_nested_dto_info_list(schema: Schema) -> list[NestedDTOInfo]:
    """Get information on nested DTOs in the schema."""
    nested_dto_info_list = []
    for field_name, field_value in schema.fields.items():
        if not isinstance(field_value, marshmallow.fields.Nested):
            continue
        metadata = field_value.metadata
        source: SourceMappingEnum = _get_required_argument("source", metadata, schema)
        _check_for_errors(metadata=metadata, source=source)
        nested_dto_class = metadata["nested_dto_class"]
        nested_dto_info_list.append(
            NestedDTOInfo(key=field_name, class_=nested_dto_class)
        )

    return nested_dto_info_list


def _get_data_from_sources(schema: Schema) -> JSONDict:
    """Get extract request data from request sources specified in the schema and field metadata."""
    data = {}
    for field_name, field_value in schema.fields.items():
        metadata: dict[
            str,
            SourceMappingEnum | str
        ] = field_value.metadata
        source: SourceMappingEnum = _get_required_argument(
            argument_name="source", metadata=metadata, schema_class=schema
        )
        source_getting_function = _get_source_getting_function(source)
        val = source_getting_function(field_name)
        if val is not None:
            data[field_name] = val

    return data


def get_source_data_info_from_sources(schema: Schema) -> SourceDataInfo:
    """Get data from sources specified in the schema and field metadata."""
    data = _get_data_from_sources(schema=schema)
    nested_dto_info_list = get_nested_dto_info_list(schema=schema)
    return SourceDataInfo(data=data, nested_dto_info_list=nested_dto_info_list)


def _check_for_errors(metadata: dict[str, Any], source: SourceMappingEnum):
    if source != SourceMappingEnum.JSON:
        raise InvalidSourceMappingError(
            "Nested fields can only be populated from JSON sources"
        )
    if "nested_dto_class" not in metadata:
        raise InvalidSourceMappingError(
            "Nested fields must have a 'nested_dto_class' metadata"
        )


def _apply_transformation_functions_to_dict(
    fields: dict,
    intermediate_data: ValidatedDict
):
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
        transformation_function: callable = metadata.get(  # pyright: ignore[reportGeneralTypeIssues]
            "transformation_function", None
        )
        if transformation_function is not None and field_name in intermediate_data:
            intermediate_data[field_name] = transformation_function(
                intermediate_data[field_name]
            )
