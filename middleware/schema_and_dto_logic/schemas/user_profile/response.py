from marshmallow import Schema, fields

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.schemas.data_requests.get.many.response import (
    GetManyDataRequestsResponseSchema,
)
from middleware.schema_and_dto_logic.schemas.search.follow import (
    GetUserFollowedSearchesSchema,
)
from middleware.schema_and_dto_logic.schemas.user_profile.external_accounts import (
    ExternalAccountsSchema,
)
from middleware.schema_and_dto_logic.schemas.user_profile.recent_searches import (
    GetUserRecentSearchesOuterSchema,
)
from middleware.schema_and_dto_logic.util import get_json_metadata


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
