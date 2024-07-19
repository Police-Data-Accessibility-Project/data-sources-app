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
