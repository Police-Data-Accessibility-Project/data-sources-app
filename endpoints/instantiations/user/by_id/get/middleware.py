from flask import make_response
from werkzeug.exceptions import Forbidden

from db.client.core import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.primary_resource_logic.user_profile import get_owner_data_requests
from middleware.schema_and_dto.dtos.common.base import GetManyBaseDTO
from middleware.security.access_info.primary import AccessInfoPrimary


def get_user_by_id_wrapper(
    db_client: DatabaseClient, user_id: int, access_info: AccessInfoPrimary
):
    _check_user_is_either_owner_or_admin(access_info, user_id)

    # Get user info
    email = db_client.get_user_email(user_id=user_id)  #
    external_accounts = db_client.get_user_external_accounts(user_id=user_id)
    recent_searches = db_client.get_user_recent_searches(user_id=user_id)
    followed_searches = db_client.get_user_followed_searches(user_id=user_id)
    data_requests = get_owner_data_requests(
        db_client=db_client, dto=GetManyBaseDTO(page=1), user_id=user_id
    )
    permissions = db_client.get_user_permissions(user_id)
    data = {
        "email": email,
        "external_accounts": external_accounts,
        "recent_searches": recent_searches,
        "followed_searches": followed_searches,
        "data_requests": data_requests,
        "permissions": [permission.value for permission in permissions],
    }
    json_body = {"data": data}

    return make_response(json_body)


def _check_user_is_either_owner_or_admin(access_info, user_id):
    if (
        user_id != access_info.get_user_id()
        and PermissionsEnum.READ_ALL_USER_INFO not in access_info.permissions
    ):
        raise Forbidden("Forbidden.")
