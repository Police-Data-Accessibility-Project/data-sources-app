from marshmallow import fields, Schema

from database_client.enums import RequestStatus
from middleware.enums import RecordType
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import DataSourceExpandedSchema
from middleware.schema_and_dto_logic.response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


class DataRequestsSchema(Schema):
    id = fields.Integer(
        metadata=get_json_metadata("The ID of the data request"),
    )
    submission_notes = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Optional notes provided by the submitter during the request submission."
        ),
    )
    request_status = fields.Enum(
        enum=RequestStatus,
        by_value=fields.Str,
        metadata=get_json_metadata(
            "The current status of the data request. Editable only by admins."
        ),
    )
    location_described_submitted = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Description of the location relevant to the request, if applicable."
        ),
    )
    archive_reason = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If applicable, the reason for archiving the data request. Viewable only by owners and admins. Editable only by admins."
        ),
    )
    date_created = fields.DateTime(
        format="iso", metadata=get_json_metadata("When the data request was created.")
    )
    date_status_last_changed = fields.DateTime(
        format="iso",
        metadata=get_json_metadata(
            "The date and time when the status of the request was last changed."
        ),
    )
    creator_user_id = fields.Integer(
        metadata=get_json_metadata("The ID of the user who created the data request.")
    )
    github_issue_url = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "If applicable, the URL to the issue on Github. Editable only by admins."
        ),
    )
    internal_notes = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Internal notes by PDAP staff about the request. Viewable and editable only by admins."
        ),
    )
    record_types_required = fields.List(
        fields.Enum(
            enum=RecordType,
            by_value=fields.Str,
            metadata=get_json_metadata(
                "The record types associated with the data request."
            ),
        ),
        allow_none=True,
        metadata=get_json_metadata(
            "Multi-select of record types from record_types taxonomy. Editable only by admins."
        ),
    )
    pdap_response = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Public notes by PDAP about the request. Editable only by admins."
        ),
    )
    coverage_range = fields.Str(
        allow_none=True,
        metadata=get_json_metadata(
            "The date range covered by the request, if applicable."
        ),
    )
    data_requirements = fields.String(
        allow_none=True,
        metadata=get_json_metadata(
            "Detailed requirements for the data being requested."
        ),
    )

class DataRequestsPostSchema(Schema):
    entry_data = fields.Nested(
        nested=DataRequestsSchema,
        metadata=get_json_metadata("The data request to be created"),
    )

class DataRequestsGetSchema(DataRequestsSchema):
    data_source_ids = fields.List(
        fields.Str(
            metadata=get_json_metadata("The data source IDs associated with the data request")
        ),
        required=True,
        metadata=get_json_metadata("The data source IDs associated with the data request"))
    data_sources = fields.List(
        fields.Nested(
            nested=DataSourceExpandedSchema,
            metadata=get_json_metadata("The data sources associated with the data request")
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the data request")
    )

class GetManyDataRequestsSchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataRequestsGetSchema,
            metadata=get_json_metadata("The list of data requests"),
        ),
        metadata=get_json_metadata("The list of results"),
    )


class GetByIDDataRequestsResponseSchema(MessageSchema):
    data = fields.Nested(
        nested=DataRequestsGetSchema,
        metadata=get_json_metadata("The data request result"),
    )
