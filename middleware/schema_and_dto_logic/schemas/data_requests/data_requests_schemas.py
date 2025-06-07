from marshmallow import fields, Schema, post_load

from db.enums import RequestStatus
from middleware.schema_and_dto_logic.schemas.data_requests.data_requests_base_schema import (
    DataRequestsSchema,
)
from middleware.schema_and_dto_logic.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.schemas.locations_schemas import (
    LocationInfoSchema,
    LocationInfoExpandedSchema,
)
from middleware.schema_and_dto_logic.schemas.typeahead_suggestion_schemas import (
    TypeaheadLocationsResponseSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GetByIDBaseSchema,
)
from middleware.schema_and_dto_logic.dtos.data_requests_dtos import (
    DataRequestLocationInfoPostDTO,
    DataRequestsPutDTO,
    RequestInfoPostDTO,
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
