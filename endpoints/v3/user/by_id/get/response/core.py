from pydantic import BaseModel, Field

from db.enums import UserCapacityEnum
from endpoints.v3.user.by_id.get.response.data_request import GetDataRequestModel
from endpoints.v3.user.by_id.get.response.external_accounts import ExternalAccountsModel
from endpoints.v3.user.by_id.get.response.followed_search import GetUserFollowedSearchModel
from endpoints.v3.user.by_id.get.response.recent_search import GetUserRecentSearchModel
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos._helpers import default_field_required


class GetUserProfileResponse(BaseModel):
    email: str = Field(
        description="The email of the user.",
    )
    external_accounts: ExternalAccountsModel = Field(
        description="The external accounts of the user.",
    )
    recent_searches: list[GetUserRecentSearchModel] = Field(
        description="The recent searches of the user.",
    )
    followed_searches: list[GetUserFollowedSearchModel] = Field(
        description="The followed searches of the user.",
    )
    data_requests: list[GetDataRequestModel] = Field(
        description="The data requests of the user.",
    )
    permissions: list[PermissionsEnum] = Field(
        description="The permissions of the user.",
    )
    capacities: list[UserCapacityEnum] = default_field_required(
        description="The capacities of the user.",
    )
