"""
These schemas are used in response validation,
and do not have DTOs associated with them.
"""

from marshmallow import Schema, fields

from middleware.schema_and_dto_logic.custom_fields import EntryDataListField, DataField
from utilities.enums import SourceMappingEnum


class IDAndMessageSchema(Schema):
    id = fields.String(
        required=True,
        metadata={
            "description": "The id of the created entry",
            "source": SourceMappingEnum.JSON,
        }
    )
    message = fields.String(
        required=True,
        metadata={
            "description": "The success message",
            "source": SourceMappingEnum.JSON,
            "example": "Success. Entry created",
        }
    )


class GetManyResponseSchema(Schema):
    message = fields.String(
        metadata={
            "description": "The success message",
            "source": SourceMappingEnum.JSON,
        }
    )
    count = fields.Integer(
        metadata={
            "description": "The total number of results",
            "source": SourceMappingEnum.JSON,
        }
    )
    data = EntryDataListField(
        fields.Dict,
        required=True,
        metadata={
            "description": "The list of results",
            "source": SourceMappingEnum.JSON,
        }
    )


class EntryDataResponseSchema(Schema):
    """
    Note: This exists as a complement to EntryDataRequestSchema,
    but with the field name and description modified.

    The modification of the field name was done to clarify that this data is being returned
    rather than provided
    """
    message = fields.String(
        required=True,
        metadata={
            "description": "The success message",
            "source": SourceMappingEnum.JSON,
            "example": "Success. Entry created",
        }
    )
    data = DataField(
        required=True,
        metadata={
            "description": "The data for the given entry",
            "source": SourceMappingEnum.JSON,
        }
    )
