from marshmallow import Schema, fields

from database_client.enums import (
    ApprovalStatus,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_sources_dtos import DataSourceEntryDataPostDTO
from middleware.schema_and_dto_logic.primary_resource_schemas.agencies_base_schemas import AgenciesExpandedSchema
from middleware.schema_and_dto_logic.common_response_schemas import (
    GetManyResponseSchemaBase,
    MessageSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_base_schema import DataRequestsSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import DataSourceExpandedSchema, \
    DataSourcesMapResponseInnerSchema
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import SourceMappingEnum


class DataSourceGetSchema(DataSourceExpandedSchema):
    """
    The schema for getting a single data source.
    Include the base schema as well as data from connected tables, including agencies and record types.
    """

    agencies = fields.List(
        fields.Nested(
            AgenciesExpandedSchema(
                only=[
                    "id",
                    "name",
                    "submitted_name",
                    "state_name",
                    "locality_name",
                    "state_iso",
                    "county_name",
                    "agency_type",
                    "jurisdiction_type",
                    "homepage_url"
                ],
            ),
            metadata=get_json_metadata("The agencies associated with the data source."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The agencies associated with the data source."),
    )
    agency_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The agency ids associated with the data source."
            ),
        ),
        metadata=get_json_metadata("The agency ids associated with the data source."),
    )
    data_requests = fields.List(
        fields.Nested(
            nested=DataRequestsSchema(),
            metadata=get_json_metadata("The data requests associated with the data source."),
        ),
        allow_none=True,
        metadata=get_json_metadata("The data requests associated with the data source."),
    )


class DataSourcesGetByIDSchema(MessageSchema):
    data = fields.Nested(
        DataSourceGetSchema,
        metadata=get_json_metadata("The result"),
    )


class DataSourcesGetManySchema(GetManyResponseSchemaBase):
    data = fields.List(
        cls_or_instance=fields.Nested(
            nested=DataSourceGetSchema,
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )


class DataSourcesPostSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=[
                "id",
                "name",
                "updated_at",
                "created_at",
                "record_type_id",
                "approval_status_updated_at",
                "broken_source_url_as_of",
                "last_approval_editor",
                "last_approval_editor_old"
            ],
            partial=True,
        ),
        required=True,
        metadata=get_json_metadata(
            description="The data source to be created",
            nested_dto_class=DataSourceEntryDataPostDTO,
        ),
    )
    linked_agency_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The agency ids associated with the data source."
            ),
        ),
        metadata=get_json_metadata("The agency ids associated with the data source."),
    )


class DataSourcesPutSchema(Schema):
    entry_data = fields.Nested(
        nested=DataSourceExpandedSchema(
            exclude=[
                "name",
                "id",
                "updated_at",
                "created_at",
                "rejection_note",
                "record_type_id",
                "data_source_request",
                "approval_status_updated_at",
                "broken_source_url_as_of",
                "last_approval_editor",
                "last_approval_editor_old"
            ]
        ),
        required=True,
        metadata=get_json_metadata("The data source to be updated"),
    )


class DataSourcesGetManyRequestSchema(GetManyRequestsBaseSchema):
    approval_status = fields.Enum(
        enum=ApprovalStatus,
        by_value=fields.String,
        required=False,
        metadata={
            "source": SourceMappingEnum.QUERY_ARGS,
            "description": "The approval status of the data sources.",
            "default": "approved",
        },
    )


class DataSourcesMapResponseSchema(MessageSchema):
    data = fields.List(
        fields.Nested(
            DataSourcesMapResponseInnerSchema(),
            metadata=get_json_metadata("The list of results"),
        ),
        metadata=get_json_metadata("The list of results"),
    )