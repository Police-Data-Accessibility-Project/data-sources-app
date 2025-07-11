from marshmallow import Schema, fields

from endpoints.instantiations.user.by_id.get.dto import ExternalAccountDTO, UserProfileResponseSchemaInnerDTO
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from endpoints.instantiations.data_requests_.get.many.schemas.response import GetManyDataRequestsResponseSchema
from middleware.schema_and_dto.schemas.search.follow import GetUserFollowedSearchesSchema
from middleware.schema_and_dto.schemas.user.recent_searches import GetUserRecentSearchesOuterSchema
from middleware.schema_and_dto.util import get_json_metadata

ExternalAccountsSchema = pydantic_to_marshmallow(ExternalAccountDTO)


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

# UserProfileResponseSchemaInner = pydantic_to_marshmallow(UserProfileResponseSchemaInnerDTO)


class UserProfileResponseSchema(Schema):
    data = fields.Nested(
        UserProfileResponseSchemaInner(),
        metadata=get_json_metadata("The result"),
    )

