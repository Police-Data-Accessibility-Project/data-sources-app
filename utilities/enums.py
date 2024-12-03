from enum import Enum


class RecordCategories(Enum):
    """
    Enum for record categories.
    """

    POLICE = "Police & Public Interactions"
    OFFICERS = "Info about Officers"
    AGENCIES = "Info about Agencies"
    RESOURCE = "Agency-published Resources"
    JAIL = "Jails & Courts"
    OTHER = "Other"
    ALL = "All"


class SourceMappingEnum(Enum):
    """
    Used to denote which sources should be derived from the request
    """

    QUERY_ARGS = "args"
    FORM = "form"
    JSON = "json"
    PATH = "path"
    FILE = "file"


class ParserLocation(Enum):
    """
    Used to denote the location a parameter is in the parser query
    """

    PATH = "path"
    QUERY = "query"
