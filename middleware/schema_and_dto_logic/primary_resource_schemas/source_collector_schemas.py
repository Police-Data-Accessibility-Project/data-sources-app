from marshmallow import Schema, fields, validate

from middleware.enums import RecordTypes, DataSourceCreationResponse
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    generate_marshmallow_schema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.source_collector_dtos import (
    SourceCollectorPostResponseInnerDTO,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class SourceCollectorPostRequestInnerSchema(Schema):
    name = fields.String(
        metadata=get_json_metadata("The name of the data source"), required=True
    )
    description = fields.String(
        metadata=get_json_metadata("The description of the data source"), required=True
    )
    source_url = fields.String(
        metadata=get_json_metadata("The URL of the data source"), required=True
    )
    record_type = fields.Enum(
        enum=RecordTypes,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata(
            "The record type of the data source.",
        ),
    )
    record_formats = fields.List(
        fields.String(
            metadata=get_json_metadata(
                "What formats the data source can be obtained in.",
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "What formats the data source can be obtained in.",
        ),
    )
    data_portal_type = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "The data portal type of the data source.",
        ),
    )
    last_approval_editor = fields.Integer(
        required=True,
        metadata=get_json_metadata(
            "User id of the user who provided approval for the data source in source collector."
        ),
    )
    supplying_entity = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If the Agency didn't publish this, who did?",
        ),
    )
    agency_ids = fields.List(
        fields.Integer(
            required=True,
            metadata=get_json_metadata(
                "The agencies that are associated with this data source."
            ),
        ),
        required=True,
        metadata=get_json_metadata(
            "The agencies that are associated with this data source."
        ),
    )


class SourceCollectorPostRequestSchema(Schema):
    data_sources = fields.List(
        fields.Nested(
            SourceCollectorPostRequestInnerSchema(),
            required=True,
            metadata=get_json_metadata("The data sources associated with the request"),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the request"),
    )


SourceCollectorPostResponseInnerSchema = generate_marshmallow_schema(
    SourceCollectorPostResponseInnerDTO
)


class SourceCollectorPostResponseSchema(MessageSchema):
    data_sources = fields.List(
        fields.Nested(
            SourceCollectorPostResponseInnerSchema(),
            required=True,
            metadata=get_json_metadata(
                "The data sources associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the data request"),
        validate=validate.Length(min=1, max=100),
    )


class SourceCollectorDuplicatesPostRequestSchema(Schema):
    urls = fields.List(
        fields.String(
            required=True,
            metadata=get_json_metadata("The URLs of the data sources to check"),
        ),
        required=True,
        metadata=get_json_metadata("The URLs of the data sources to check"),
        validate=validate.Length(min=1, max=100),
    )


class SourceCollectorDuplicatePostResponseSchema(Schema):
    results = fields.Dict(
        keys=fields.String(
            required=True,
            metadata=get_json_metadata("The URLs of the data sources to check"),
        ),
        values=fields.Boolean(
            required=True,
            metadata=get_json_metadata("The results of the duplicate check"),
        ),
        required=True,
        metadata=get_json_metadata(
            "The results of the duplicate check",
        ),
    )
