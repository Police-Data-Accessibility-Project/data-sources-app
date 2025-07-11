from typing import Union

from marshmallow import fields

from middleware.enums import JurisdictionType
from middleware.schema_and_dto.dtos.agencies.put import AgencyInfoPutDTO
from middleware.schema_and_dto.dtos.agencies.post import AgencyInfoPostDTO
from middleware.schema_and_dto.schemas.agencies.base import AgencyInfoBaseSchema
from utilities.enums import SourceMappingEnum


def get_name_field(required: bool) -> fields.Str:
    return fields.Str(
        required=required,
        metadata={
            "description": "The name of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


def get_jurisdiction_type_field(required: bool) -> fields.Enum:
    return fields.Enum(
        required=required,
        enum=JurisdictionType,
        by_value=fields.Str,
        metadata={
            "description": "The highest level of jurisdiction of the agency.",
            "source": SourceMappingEnum.JSON,
        },
    )


def get_agency_info_field(
    schema: type[AgencyInfoBaseSchema],  # pyright: ignore[reportInvalidTypeForm]
    nested_dto_class: type[Union[AgencyInfoPutDTO, AgencyInfoPostDTO]],
) -> fields.Nested:
    return fields.Nested(
        schema,
        required=True,
        metadata={
            "description": "Information about the agency",
            "source": SourceMappingEnum.JSON,
            "nested_dto_class": nested_dto_class,
        },
    )
