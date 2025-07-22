from endpoints.instantiations.user._shared.dtos.recent_searches import (
    GetUserRecentSearchesDTO,
)
from middleware.schema_and_dto.dtos.dto_helpers import create_get_many_dto

GetUserRecentSearchesOuterDTO = create_get_many_dto(
    data_list_dto=GetUserRecentSearchesDTO,
    description="The recent searches of the user.",
)
