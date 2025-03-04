from marshmallow import Schema, fields, validate

from database_client.enums import UpdateFrequency
from middleware.schema_and_dto_logic.util import get_json_metadata
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
    )


class ArchivesGetResponseSchema(Schema):
    id = fields.Integer(
        required=True, metadata=get_json_metadata("The ID of the archive")
    )
    last_cached = fields.DateTime(
        required=True,
        metadata=get_json_metadata("The last date the archive was cached"),
    )
    source_url = fields.String(
        required=True, metadata=get_json_metadata("The URL of the archive")
    )
    update_frequency = fields.String(
        required=True, metadata=get_json_metadata("The archive update frequency")
    )


class ArchivesPutRequestSchema(Schema):
    id = fields.String(
        required=True, metadata=get_json_metadata("The ID of the archive")
    )
    last_cached = fields.DateTime(
        required=True,
        metadata=get_json_metadata("The last date the archive was cached"),
    )
    broken_source_url_as_of = fields.Date(
        required=True,
        metadata=get_json_metadata("The date the source was marked as broken"),
    )
