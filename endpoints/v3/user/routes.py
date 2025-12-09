from fastapi import APIRouter, Depends

from endpoints.v3.user.by_id.get.response.core import GetUserProfileResponse
from endpoints.v3.user.by_id.get.wrapper import get_user_by_id_wrapper
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.fastapi import get_standard_access_info

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/{user_id}")
def get_user(
    user_id: int,
    access_info: AccessInfoPrimary = Depends(get_standard_access_info),
) -> GetUserProfileResponse:
    return get_user_by_id_wrapper(
        user_id=user_id,
        access_info=access_info,
    )
