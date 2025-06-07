from marshmallow import fields, Schema, post_load, validate

from db.enums import RequestStatus, RequestUrgency
from middleware.enums import RecordTypes
from middleware.primary_resource_logic.data_requests import RequestInfoPostDTO
from middleware.schema_and_dto_logic.schemas.typeahead_suggestion_schemas import (
    TypeaheadLocationsResponseSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    LocationInfoSchema,
    GetManyRequestsBaseSchema,
    GetByIDBaseSchema,
    LocationInfoExpandedSchema,
)
from middleware.schema_and_dto_logic.dtos.data_requests_dtos import (
    DataRequestLocationInfoPostDTO,
    DataRequestsPutDTO,
)
from middleware.schema_and_dto_logic.schemas.data_sources_schemas import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.schema_helpers import (
    create_get_many_schema,
    create_get_by_id_schema,
)
from middleware.schema_and_dto_logic.util import (
    get_json_metadata,
    get_query_metadata,
    get_path_metadata,
)


class DataRequestsSchema(Schema):
    """
    Reflects the columns in the `data_requests` database table
    """

    id = fields.Integer(
        metadata=get_json_metadata("The ID of the data request"),
    )
    title = fields.String(
        metadata=get_json_metadata("The title of the data request"),
        required=True,
        validate=validate.Length(min=1, max=255),
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
    github_issue_number = fields.Integer(
        allow_none=True,
        metadata=get_json_metadata(
            "If applicable, the number of the issue on Github. Editable only by admins."
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
            enum=RecordTypes,
            by_value=fields.Str,
            metadata=get_json_metadata(
                "The record types associated with the data request. Editable only by admins."
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
    request_urgency = fields.Enum(
        enum=RequestUrgency,
        by_value=fields.Str,
        metadata=get_json_metadata("The urgency of the request."),
    )


class DataRequestsGetSchemaBase(DataRequestsSchema):
    data_sources = fields.List(
        fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "submitted_name"]),
            metadata=get_json_metadata(
                "The data sources associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the data request"),
    )
    data_source_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The data source ids associated with the data request."
            ),
        ),
        metadata=get_json_metadata(
            "The data source ids associated with the data request."
        ),
    )
    locations = fields.List(
        fields.Nested(
            nested=LocationInfoSchema(),
            metadata=get_json_metadata(
                "The locations associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The locations associated with the data request"),
    )
    location_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The location ids associated with the data request."
            ),
        ),
        metadata=get_json_metadata(
            "The location ids associated with the data request."
        ),
    )


class DataRequestsPutSchema(Schema):
    entry_data = fields.Nested(
        nested=DataRequestsSchema(
            exclude=[
                "id",
                "date_created",
                "date_status_last_changed",
                "creator_user_id",
            ],
            partial=True,
        ),
        metadata=get_json_metadata(
            "The information about the data request to be updated",
            nested_dto_class=DataRequestsPutDTO,
        ),
        required=True,
    )


class DataRequestsPostSchema(Schema):
    request_info = fields.Nested(
        nested=DataRequestsSchema(
            only=[
                "title",
                "submission_notes",
                "data_requirements",
                "request_urgency",
                "coverage_range",
            ]
        ),
        metadata=get_json_metadata(
            "The information about the data request to be created",
            nested_dto_class=RequestInfoPostDTO,
        ),
        required=True,
    )
    location_infos = fields.List(
        fields.Nested(
            nested=TypeaheadLocationsResponseSchema(
                exclude=["display_name", "location_id"]
            ),
            metadata=get_json_metadata(
                "The locations associated with the data request",
                nested_dto_class=DataRequestLocationInfoPostDTO,
            ),
        ),
        required=False,
        allow_none=True,
        metadata=get_json_metadata("The locations associated with the data request"),
    )

    @post_load
    def location_infos_convert_empty_list_to_none(self, in_data, **kwargs):
        location_infos = in_data.get("location_infos", None)
        if location_infos == []:
            in_data["location_infos"] = None
        return in_data


class GetManyDataRequestsRequestsSchema(GetManyRequestsBaseSchema):
    request_status = fields.Enum(
        enum=RequestStatus,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_query_metadata("The status of the requests to return."),
    )


GetManyDataRequestsResponseSchema = create_get_many_schema(
    data_list_schema=DataRequestsGetSchemaBase,
    description="The list of data requests",
)

GetByIDDataRequestsResponseSchema = create_get_by_id_schema(
    data_schema=DataRequestsGetSchemaBase,
    description="The data request result",
)

GetManyDataRequestsRelatedLocationsSchema = create_get_many_schema(
    data_list_schema=LocationInfoExpandedSchema,
    description="The list of locations associated with the data request",
)


class DataRequestsRelatedLocationAddRemoveSchema(GetByIDBaseSchema):
    location_id = fields.Integer(
        required=True,
        metadata=get_path_metadata(
            "The ID of the location to add or remove from the data request."
        ),
    )
