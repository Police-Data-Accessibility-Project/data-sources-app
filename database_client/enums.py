"""
Enums utilized within the Database Client
"""

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


class RequestStatus(Enum):
    """
    Correlates to the request_status enum in the database
    """

    INTAKE = "Intake"
    ACTIVE = "Active"
    COMPLETE = "Complete"
    REQUEST_WITHDRAWN = "Request withdrawn"
    WAITING_FOR_SCRAPER = "Waiting for scraper"
    ARCHIVED = "Archived"
    READY_TO_START = "Ready to start"
    WAITING_FOR_FOIA = "Waiting for FOIA"
    WAITING_FOR_REQUESTOR = "Waiting for requestor"


class DetailLevel(Enum):
    """
    Correlates to the detail_level enum in the database
    """

    INDIVIDUAL = "Individual record"
    AGGREGATED = "Aggregated records"
    SUMMARIZED = "Summarized totals"


class AccessType(Enum):
    """
    Correlates to the access_type enum in the database
    """

    WEB_PAGE = "Webpage"
    DOWNLOAD = "Download"
    API = "API"


class RetentionSchedule(Enum):
    """
    Correlates to the retention_schedule enum in the database
    """

    ONE_TO_TEN_YEARS = "1-10 years"
    LESS_THAN_ONE_WEEK = "< 1 week"
    ONE_DAY = "1 day"
    FUTURE_ONLY = "Future only"
    LESS_THAN_ONE_DAY = "< 1 day"
    LESS_THAN_ONE_YEAR = "< 1 year"
    ONE_MONTH = "1 month"
    ONE_WEEK = "1 week"
    GREATER_THAN_TEN_YEARS = "> 10 years"


class URLStatus(Enum):
    """
    Correlates to the url_status enum in the database
    """

    AVAILABLE = "available"
    BROKEN = "broken"
    OK = "ok"
    NONE_FOUND = "none found"


class UpdateMethod(Enum):
    """
    Correlates to the update_method enum in the database
    """

    INSERT = "Insert"
    NO_UPDATES = "No updates"
    OVERWRITE = "Overwrite"


class AgencyAggregation(Enum):
    """
    Correlates to the agency_aggregation enum in the database
    """

    COUNTY = "county"
    LOCAL = "local"
    STATE = "state"
    FEDERAL = "federal"


class RequestUrgency(Enum):
    """
    Correlates to the request_urgency enum in the database
    """

    URGENT = "urgent"  # Less than a week
    SOMEWHAT_URGENT = "somewhat_urgent"  # Less than a month
    NOT_URGENT = "not_urgent"  # A few months
    LONG_TERM = "long_term"  # A year or more
    INDEFINITE = "indefinite_unknown"  # Indefinite or unknown length of time


class EntityType(Enum):
    DATA_SOURCE = "Data Source"
    DATA_REQUEST = "Data Request"


class EventType(Enum):
    REQUEST_READY_TO_START = "Request Ready to Start"
    REQUEST_COMPLETE = "Request Complete"
    DATA_SOURCE_APPROVED = "Data Source Approved"
