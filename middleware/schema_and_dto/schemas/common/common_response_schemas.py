"""
These schemas are used in response validation,
and do not have DTOs associated with them.
"""

from marshmallow import Schema, fields

from middleware.schema_and_dto.dtos.common_dtos import MessageDTO, IDAndMessageDTO, \
    GetManyResponseDTOBase, GetManyResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.common.custom_fields import (
    EntryDataListField,
    DataField,
)
from utilities.enums import SourceMappingEnum

MessageSchema = pydantic_to_marshmallow(MessageDTO)

IDAndMessageSchema = pydantic_to_marshmallow(IDAndMessageDTO)

GetManyResponseSchemaBase = pydantic_to_marshmallow(GetManyResponseDTOBase)

GetManyResponseSchema = pydantic_to_marshmallow(GetManyResponseDTO)

class EntryDataResponseSchema(MessageSchema):
    """
    Note: This exists as a complement to EntryDataRequestSchema,
    but with the field name and description modified.

    The modification of the field name was done to clarify that this data is being returned
    rather than provided
    """

    data = DataField(
        required=True,
        metadata={
            "description": "The data for the given entry",
            "source": SourceMappingEnum.JSON,
        },
    )
