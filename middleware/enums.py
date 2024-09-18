from enum import Enum, auto


class CallbackFunctionsEnum(Enum):
    """
    Enums for the callback_wrapper function, to determine
    which callback function to use.
    """

    LOGIN_WITH_GITHUB = "login_user_with_github"
    CREATE_USER_WITH_GITHUB = "register_user"
    LINK_TO_GITHUB = "link_to_github"


class PermissionsEnum(Enum):
    """
    Enums for the permissions logic.
    """

    DB_WRITE = "db_write"
    READ_ALL_USER_INFO = "read_all_user_info"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class PermissionsActionEnum(Enum):
    ADD = "add"
    REMOVE = "remove"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class AccessTypeEnum(Enum):
    JWT = auto()
    API_KEY = auto()

class Relations(Enum):
    """
    A list of valid relations for the database
    """
    DATA_REQUESTS = "data_requests"
    AGENCIES = "agencies"
    DATA_SOURCES = "data_sources"
    RELATED_SOURCES = "link_data_sources_data_requests"
    AGENCIES_EXPANDED = "agencies_expanded"
    TEST_TABLE = "test_table"

class JurisdictionType(Enum):
    """
    A list of valid agency jurisdiction types
    """
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    LOCAL = "local"
    PORT = "port"
    TRIBAL = "tribal"
    TRANSIT = "transit"
    SCHOOL = "school"
    NONE = None


class JurisdictionSimplified(Enum):
    """
    A simplified list of jurisdictions utilized in organizing search results
    """
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    LOCALITY = "locality"

class AgencyType(Enum):
    """
    A list of valid agency types
    """
    NONE = None
    AGGREGATED = "aggregated"
    COURT = "court"
    LAW_ENFORCEMENT_POLICE = "law enforcement/police"
    CORRECTIONS = "corrections"