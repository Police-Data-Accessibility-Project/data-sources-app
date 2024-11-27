from marshmallow import Schema, fields

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_advanced_schemas import (
    GetManyDataRequestsResponseSchema,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import (
    GetUserFollowedSearchesSchema,
)
from middleware.schema_and_dto_logic.schema_helpers import create_get_many_schema
from middleware.schema_and_dto_logic.util import get_json_metadata
from utilities.enums import RecordCategories


class UserPutSchema(Schema):
    old_password = fields.Str(
        required=True,
        metadata=get_json_metadata("The old password of the user"),
    )
    new_password = fields.Str(
        required=True,
        metadata=get_json_metadata("The new password of the user"),
    )


class GetUserRecentSearchesInnerSchema(Schema):
    state_iso = fields.Str(
        required=True,
        metadata=get_json_metadata("The state of the search."),
    )
    county_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The county of the search, if any."),
    )
    locality_name = fields.Str(
        required=True,
        allow_none=True,
        metadata=get_json_metadata("The locality of the search, if any."),
    )
    location_type = fields.Str(
        required=True, metadata=get_json_metadata("The type of location of the search")
    )
    record_categories = fields.List(
        fields.Enum(
            enum=RecordCategories,
            by_value=fields.Str,
            metadata=get_json_metadata("The record categories of the search."),
        ),
        required=True,
        metadata=get_json_metadata("The record categories of the search."),
    )


GetUserRecentSearchesOuterSchema = create_get_many_schema(
    data_list_schema=GetUserRecentSearchesInnerSchema(),
    description="The list of recent searches for the user",
)


class ExternalAccountsSchema(Schema):
    github = fields.Str(
        required=True,
        metadata=get_json_metadata("The GitHub user id of the user"),
    )


class UserProfileResponseSchemaInner(Schema):
    email = fields.Str(
        required=True,
        metadata=get_json_metadata("The email of the user"),
    )
    external_accounts = fields.Nested(
        ExternalAccountsSchema(),
        required=True,
        metadata=get_json_metadata("The external accounts of the user"),
    )
    recent_searches = fields.Nested(
        GetUserRecentSearchesOuterSchema(exclude=["message"]),
        required=True,
        metadata=get_json_metadata("The recent searches of the user"),
    )
    followed_searches = fields.Nested(
        GetUserFollowedSearchesSchema(exclude=["message"]),
        required=True,
        metadata=get_json_metadata("The followed searches of the user"),
    )
    data_requests = fields.Nested(
        GetManyDataRequestsResponseSchema(exclude=["message"]),
        required=True,
        metadata=get_json_metadata("The data requests of the user"),
    )
    permissions = fields.List(
        fields.Enum(
            enum=PermissionsEnum,
            by_value=fields.Str,
            metadata=get_json_metadata("The permissions of the user"),
        ),
        required=True,
        metadata=get_json_metadata("The permissions of the user"),
    )


class UserProfileResponseSchema(Schema):
    data = fields.Nested(
        UserProfileResponseSchemaInner(),
        metadata=get_json_metadata("The result"),
    )
