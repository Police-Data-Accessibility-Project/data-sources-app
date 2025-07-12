from typing import Optional

from pydantic import BaseModel

from db.enums import UserCapacityEnum
from endpoints.instantiations.data_requests_.get.many.dtos.response import GetManyDataRequestsResponseDTO
from endpoints.instantiations.search._shared.dtos.follow import GetUserFollowedSearchesDTO
from endpoints.instantiations.user.by_id.get.recent_searches.dto import GetUserRecentSearchesOuterDTO
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos._helpers import default_field_required


class ExternalAccountDTO(BaseModel):
    github: Optional[str] = default_field_required(description="The GitHub user id of the user")

class UserProfileResponseSchemaInnerDTO(BaseModel):
    email: str = default_field_required(description="The email of the user")
    external_accounts: ExternalAccountDTO = default_field_required(description="The external accounts of the user")
    recent_searches: GetUserRecentSearchesOuterDTO = default_field_required(description="The recent searches of the user")
    followed_searches: GetUserFollowedSearchesDTO = default_field_required(description="The followed searches of the user")
    data_requests: GetManyDataRequestsResponseDTO = default_field_required(description="The data requests of the user")
    permissions: list[PermissionsEnum] = default_field_required(description="The permissions of the user")
    capacities: list[UserCapacityEnum] = default_field_required(description="The capacities of the user")
