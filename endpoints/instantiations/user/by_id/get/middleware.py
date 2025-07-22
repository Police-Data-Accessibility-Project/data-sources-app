from flask import make_response
from werkzeug.exceptions import Forbidden

from db.client.core import DatabaseClient
from middleware.enums import PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def get_user_by_id_wrapper(
    db_client: DatabaseClient, user_id: int, access_info: AccessInfoPrimary
):
    _check_user_is_either_owner_or_admin(access_info, user_id)

    inner_dto = db_client.get_user_profile(user_id=user_id)
    json_body = {"data": inner_dto.model_dump(mode="json")}

    return make_response(json_body)


def _check_user_is_either_owner_or_admin(access_info, user_id):
    if (
        user_id != access_info.get_user_id()
        and PermissionsEnum.READ_ALL_USER_INFO not in access_info.permissions
    ):
        raise Forbidden("Forbidden.")
