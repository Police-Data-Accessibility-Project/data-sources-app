from enum import Enum

class RelationRoleEnum(Enum):
    """
    Correlates to the relation_role enum in the database
    """
    OWNER = "OWNER"
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"

class ColumnPermissionEnum(Enum):
    """
    Correlates to the access_permission enum in the database
    """
    READ = "READ"
    WRITE = "WRITE"
    NONE = "NONE"


class ExternalAccountTypeEnum(Enum):
    GITHUB = "github"

