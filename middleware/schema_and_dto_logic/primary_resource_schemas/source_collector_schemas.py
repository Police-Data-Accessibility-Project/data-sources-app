from marshmallow import Schema, fields, validate

from middleware.enums import RecordTypes, DataSourceCreationResponse
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
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


class SourceCollectorPostResponseInnerSchema(Schema):
    url = fields.String(
        metadata=get_json_metadata("The URL of the data source"), required=True
    )
    status = fields.Enum(
        enum=DataSourceCreationResponse,
        by_value=fields.Str,
        metadata=get_json_metadata("The resulting status of the data source creation"),
    )
    data_source_id = fields.Integer(
        metadata=get_json_metadata(
            "The ID of the newly created data source, if successful."
        ),
        allow_none=True,
    )
    error = fields.String(
        metadata=get_json_metadata(
            "The error messages associated with the data source, if any"
        ),
        allow_none=True,
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
