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

class SortOrder(Enum):
    """
    Designates the order in which sorted results should be returned
    """
    ASCENDING = "ASC"
    DESCENDING = "DESC"

class ApprovalStatus(Enum):
    """
    Correlates to approval status in the `data_sources` column in the database
    """
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NEEDS_IDENTIFICATION = "needs identification"

class LocationType(Enum):
    """
    Correlates to the location_type enum in the database
    """
    STATE = "State"
    COUNTY = "County"
    LOCALITY = "Locality"