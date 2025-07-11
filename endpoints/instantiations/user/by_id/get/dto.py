from pydantic import BaseModel

from endpoints.instantiations.data_requests_._shared.dtos.base import DataRequestsBaseDTO
from endpoints.instantiations.search._shared.dtos.follow import FollowSearchResponseDTO
from endpoints.instantiations.user._shared.dtos.recent_searches import GetUserRecentSearchesDTO
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos._helpers import default_field_required


class ExternalAccountDTO(BaseModel):
    github: str = default_field_required(description="The GitHub user id of the user")

class UserProfileResponseSchemaInnerDTO(BaseModel):
    email: str = default_field_required(description="The email of the user")
    external_accounts: ExternalAccountDTO = default_field_required(description="The external accounts of the user")
    recent_searches: list[GetUserRecentSearchesDTO] = default_field_required(description="The recent searches of the user")
    followed_searches: list[FollowSearchResponseDTO] = default_field_required(description="The followed searches of the user")
    data_requests: list[DataRequestsBaseDTO] = default_field_required(description="The data requests of the user")
    permissions: list[PermissionsEnum] = default_field_required(description="The permissions of the user")