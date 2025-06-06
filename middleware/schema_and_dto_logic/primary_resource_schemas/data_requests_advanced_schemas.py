from marshmallow import fields, Schema, post_load, pre_load

from db.enums import RequestStatus
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_base_schema import (
    DataRequestsSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.typeahead_suggestion_schemas import (
    TypeaheadLocationsResponseSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyRequestsBaseSchema,
    GetByIDBaseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.locations_schemas import (
    LocationInfoSchema,
    LocationInfoExpandedSchema,
    LocationInfoResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_dtos.data_requests_dtos import (
    DataRequestLocationInfoPostDTO,
    DataRequestsPutDTO,
    RequestInfoPostDTO,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_base_schemas import (
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
from utilities.enums import SourceMappingEnum


class DataRequestsGetSchemaBase(DataRequestsSchema):
    data_sources = fields.List(
        fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "name"]),
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
            nested=LocationInfoResponseSchema(),
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
    location_ids = fields.List(
        fields.Integer(
            metadata=get_json_metadata(
                "The location ids associated with the data request",
            ),
        ),
        required=False,
        allow_none=True,
        metadata=get_json_metadata("The location ids associated with the data request"),
    )

    @post_load
    def location_ids_convert_empty_list_to_none(self, in_data, **kwargs):
        location_ids = in_data.get("location_ids", None)
        if location_ids == []:
            in_data["location_ids"] = None
        return in_data


class GetManyDataRequestsRequestsSchema(GetManyRequestsBaseSchema):
    request_statuses = fields.List(
        fields.Enum(
            enum=RequestStatus,
            by_value=fields.Str,
            allow_none=True,
            metadata=get_query_metadata("The status of the requests to return."),
        ),
        metadata=get_query_metadata("The status of the requests to return."),
    )

    @pre_load
    def listify_request_statuses(self, in_data, **kwargs):
        request_statuses = in_data.get("request_statuses", None)
        if request_statuses is None:
            return in_data
        in_data["request_statuses"] = request_statuses.split(",")

        return in_data


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


class RelatedSourceByIDSchema(GetByIDBaseSchema):
    data_source_id = fields.Str(
        required=True,
        metadata={
            "description": "The ID of the data source",
            "source": SourceMappingEnum.PATH,
        },
    )
