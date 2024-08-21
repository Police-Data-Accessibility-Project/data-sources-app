from database_client.database_client import DatabaseClient
from database_client.enums import ColumnPermissionEnum, RelationRoleEnum
from middleware.access_logic import AccessInfo
from middleware.enums import AccessTypeEnum, PermissionsEnum


def get_data_requests_relation_role(
    db_client: DatabaseClient,
    data_request_id: int,
    access_info: AccessInfo
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
    user_id = db_client.get_user_id(access_info.user_email)
    if db_client.user_is_creator_of_data_request(
        user_id=user_id,
        data_request_id=data_request_id
    ):
        return RelationRoleEnum.OWNER
    return RelationRoleEnum.STANDARD
