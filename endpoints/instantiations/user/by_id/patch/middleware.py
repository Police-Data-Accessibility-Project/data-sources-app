from flask import Response
from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from middleware.common_response_formatting import message_response
from middleware.enums import PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def _is_admin_or_owner(access_info: AccessInfoPrimary, user_id: int) -> bool:
    if access_info.has_permission(PermissionsEnum.USER_CREATE_UPDATE):
        return True
    if access_info.user_id == user_id:
        return True
    return False


def patch_user(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    user_id: int,
    dto: UserPatchDTO,
) -> Response:
    if not _is_admin_or_owner(access_info, user_id):
        raise BadRequest("You do not have permission to patch this user.")
    db_client.patch_user(user_id, dto)
    return message_response("User patched.")
