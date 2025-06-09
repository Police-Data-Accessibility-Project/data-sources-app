from marshmallow import Schema, fields, validate

from db.enums import UpdateFrequency
from utilities.enums import SourceMappingEnum


class ArchivesGetRequestSchema(Schema):
    page = fields.Integer(
        validate=validate.Range(min=1),
        load_default=1,
        metadata={
            "description": "The page number of the results to retrieve. Begins at 1.",
            "source": SourceMappingEnum.QUERY_ARGS,
        },
    )
    update_frequency = fields.Enum(
        enum=UpdateFrequency,
        by_value=fields.Str,
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The archive update frequency",
        },
    )
    last_archived_before = fields.DateTime(
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The date before which the url was archived (non-inclusive). Example: 2020-07-10",
        },
        format="%Y-%m-%d",
    )
