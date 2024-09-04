"""
These schemas are used in response validation,
and do not have DTOs associated with them.
"""

from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.custom_fields import EntryDataListField, DataField
from utilities.enums import SourceMappingEnum


class IDAndMessageSchema(Schema):
    id = fields.String(
        description="The id of the created entry",
        required=True,
        source=SourceMappingEnum.JSON,
    )
    message = fields.String(
        description="The success message",
        example="Success. Entry created",
        required=True,
        source=SourceMappingEnum.JSON,
    )


class GetManyResponseSchema(Schema):
    message = fields.String(
        description="The success message",
        source=SourceMappingEnum.JSON,
    )
    count = fields.Integer(
        description="The total number of results",
        source=SourceMappingEnum.JSON,
    )
    data = EntryDataListField(
        fields.Dict,
        description="The list of results",
        required=True,
        source=SourceMappingEnum.JSON,
    )


class EntryDataResponseSchema(Schema):
    """
    Note: This exists as a complement to EntryDataRequestSchema,
    but with the field name and description modified.

    The modification of the field name was done to clarify that this data is being returned
    rather than provided
    """
    message = fields.String(
        description="The success message",
        example="Success. Entry created",
        required=True,
        source=SourceMappingEnum.JSON,
    )
    data = DataField(
        required=True,
        description="The data for the given entry",
        source=SourceMappingEnum.JSON,
    )
