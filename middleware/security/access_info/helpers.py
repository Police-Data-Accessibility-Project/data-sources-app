from db.enums import RelationRoleEnum
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def get_relation_role(access_info: AccessInfoPrimary) -> RelationRoleEnum:
    if access_info.access_type == AccessTypeEnum.API_KEY:
        return RelationRoleEnum.STANDARD
    if PermissionsEnum.DB_WRITE in access_info.permissions:
        return RelationRoleEnum.ADMIN
    return RelationRoleEnum.STANDARD
