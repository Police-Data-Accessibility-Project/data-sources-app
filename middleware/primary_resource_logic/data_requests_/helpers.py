from werkzeug.exceptions import Forbidden

from db.client.core import DatabaseClient
from db.enums import RelationRoleEnum
from db.subquery_logic import SubqueryParameters, SubqueryParameterManager
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def check_has_admin_or_owner_role(relation_role: RelationRoleEnum):
    if relation_role not in [RelationRoleEnum.OWNER, RelationRoleEnum.ADMIN]:
        raise Forbidden("User does not have permission to perform this action.")


def is_creator_or_admin(
    access_info: AccessInfoPrimary,
    data_request_id: int,
    db_client: DatabaseClient,
):
    user_id = access_info.get_user_id()
    return (
        db_client.user_is_creator_of_data_request(
            user_id=user_id, data_request_id=data_request_id
        )
        or PermissionsEnum.DB_WRITE in access_info.permissions
    )


def get_data_requests_subquery_params() -> list[SubqueryParameters]:
    return [
        SubqueryParameterManager.data_sources(),
        SubqueryParameterManager.locations(),
    ]


def get_data_requests_relation_role(
    db_client: DatabaseClient,
    data_request_id: int | None,
    access_info: AccessInfoPrimary,
) -> RelationRoleEnum:
    """
    Determine the relation role for information on a data request
    :param db_client:
    :param data_request_id:
    :param access_info:
    :return:
    """
    if access_info.access_type == AccessTypeEnum.API_KEY:
        return RelationRoleEnum.STANDARD
    if PermissionsEnum.DB_WRITE in access_info.permissions:
        return RelationRoleEnum.ADMIN
    if data_request_id is None:
        return RelationRoleEnum.STANDARD

    # Check ownership
    user_id = access_info.get_user_id()
    if db_client.user_is_creator_of_data_request(
        user_id=user_id, data_request_id=data_request_id
    ):
        return RelationRoleEnum.OWNER
    return RelationRoleEnum.STANDARD
