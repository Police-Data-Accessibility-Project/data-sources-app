from enum import Enum, auto


class CallbackFunctionsEnum(Enum):
    """
    Enums for the callback_wrapper function, to determine
    which callback function to use.
    """

    LOGIN_WITH_GITHUB = "login_user_with_github"
    LINK_TO_GITHUB = "link_to_github"


class PermissionsEnum(Enum):
    """
    Enums for the permissions logic.
    """

    DB_WRITE = "db_write"
    READ_ALL_USER_INFO = "read_all_user_info"
    NOTIFICATIONS = "notifications"
    SOURCE_COLLECTOR = "source_collector"
    USER_CREATE_UPDATE = "user_create_update"

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
    RESET_PASSWORD = auto()
    VALIDATE_EMAIL = auto()
    NO_AUTH = auto()


class OutputFormatEnum(Enum):
    JSON = "json"
    CSV = "csv"


class Relations(Enum):
    """
    A list of valid relations for the database
    """

    DATA_REQUESTS_EXPANDED = "data_requests_expanded"
    DATA_REQUESTS = "data_requests"
    DATA_REQUESTS_GITHUB_ISSUE_INFO = "data_requests_github_issue_info"
    AGENCIES = "agencies"
    LINK_AGENCIES_DATA_SOURCES = "link_agencies_data_sources"
    DATA_SOURCES = "data_sources"
    DATA_SOURCES_EXPANDED = "data_sources_expanded"
    DATA_SOURCES_ARCHIVE_INFO = "data_sources_archive_info"
    LINK_DATA_SOURCES_DATA_REQUESTS = "link_data_sources_data_requests"
    LINK_USER_FOLLOWED_LOCATION = "link_user_followed_location"
    LINK_LOCATIONS_DATA_REQUESTS = "link_locations_data_requests"
    RECORD_CATEGORIES = "record_categories"
    RECORD_TYPES = "record_types"
    RELATED_SOURCES = "link_data_sources_data_requests"
    RESET_TOKENS = "reset_tokens"
    AGENCIES_EXPANDED = "agencies_expanded"
    EXTERNAL_ACCOUNTS = "external_accounts"
    TEST_TABLE = "test_table"
    US_STATES = "us_states"
    COUNTIES = "counties"
    LOCALITIES = "localities"
    LOCATIONS = "locations"
    LOCATIONS_EXPANDED = "locations_expanded"
    USERS = "users"
    PENDING_USERS = "pending_users"
    DEPENDENT_LOCATIONS = "dependent_locations"
    QUALIFYING_NOTIFICATIONS = "qualifying_notifications"
    USER_PENDING_NOTIFICATIONS = "user_pending_notifications"
    USER_NOTIFICATION_QUEUE = "user_notification_queue"
    RECENT_SEARCHES = "recent_searches"
    RECENT_SEARCHES_EXPANDED = "recent_searches_expanded"
    LINK_RECENT_SEARCH_RECORD_CATEGORIES = "link_recent_search_record_categories"


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
    POLICE = "police"
    JAIL = "jail"


class RecordType(Enum):
    ACCIDENT_REPORTS = "Accident Reports"
    ARREST_RECORDS = "Arrest Records"
    CALLS_FOR_SERVICE = "Calls for Service"
    CAR_GPS = "Car GPS"
    CITATIONS = "Citations"
    DISPATCH_LOGS = "Dispatch Logs"
    DISPATCH_RECORDINGS = "Dispatch Recordings"
    FIELD_CONTACTS = "Field Contacts"
    INCIDENT_REPORTS = "Incident Reports"
    MISC_POLICE_ACTIVITY = "Misc Police Activity"
    OFFICER_INVOLVED_SHOOTINGS = "Officer Involved Shootings"
    STOPS = "Stops"
    SURVEYS = "Surveys"
    USE_OF_FORCE_REPORTS = "Use of Force Reports"
    VEHICLE_PURSUITS = "Vehicle Pursuits"
    COMPLAINTS_MISCONDUCT = "Complaints & Misconduct"
    DAILY_ACTIVITY_LOGS = "Daily Activity Logs"
    TRAINING_HIRING_INFO = "Training & Hiring Info"
    PERSONNEL_RECORDS = "Personnel Records"
    ANNUAL_MONTHLY_REPORTS = "Annual & Monthly Reports"
    BUDGETS_FINANCES = "Budgets & Finances"
    CONTACT_INFO_AGENCY_META = "Contact Info & Agency Meta"
    GEOGRAPHIC = "Geographic"
    LIST_OF_DATA_SOURCES = "List of Data Sources"
    POLICIES_CONTRACTS = "Policies & Contracts"
    CRIME_MAPS_REPORTS = "Crime Maps & Reports"
    CRIME_STATISTICS = "Crime Statistics"
    MEDIA_BULLETINS = "Media Bulletins"
    RECORDS_REQUEST_INFO = "Records Request Info"
    RESOURCES = "Resources"
    SEX_OFFENDER_REGISTRY = "Sex Offender Registry"
    WANTED_PERSONS = "Wanted Persons"
    BOOKING_REPORTS = "Booking Reports"
    COURT_CASES = "Court Cases"
    INCARCERATION_RECORDS = "Incarceration Records"
    OTHER = "Other"
