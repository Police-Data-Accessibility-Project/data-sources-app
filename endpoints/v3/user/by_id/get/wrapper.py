from http import HTTPStatus

from fastapi import HTTPException

from db.queries.helpers import run_query_builder
from endpoints.v3.user.by_id.get.queries.core import GetUserByIdQueryBuilder
from endpoints.v3.user.by_id.get.response.core import GetUserProfileResponse
from middleware.enums import PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def _check_user_is_either_owner_or_admin(access_info, user_id):
    if (
        user_id != access_info.get_user_id()
        and PermissionsEnum.READ_ALL_USER_INFO not in access_info.permissions
    ):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Forbidden."
        )



def get_user_by_id_wrapper(
    user_id: int,
    access_info: AccessInfoPrimary,
) -> GetUserProfileResponse:
    _check_user_is_either_owner_or_admin(access_info, user_id=user_id)
    return run_query_builder(
        GetUserByIdQueryBuilder(
            user_id=user_id
        )
    )
