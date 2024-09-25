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

class RecordType(Enum):
    DISPATCH_RECORDINGS = "Dispatch Recordings"
    ARREST_RECORDS = "Arrest Records"
    CITATIONS = "Citations"
    INCARCERATION_RECORDS = "Incarceration Records"
    BOOKING_REPORTS = "Booking Reports"
    BUDGETS_AND_FINANCES = "Budgets & Finances"
    MISC_POLICE_ACTIVITY = "Misc Police Activity"
    GEOGRAPHIC = "Geographic"
    CRIME_MAPS_AND_REPORTS = "Crime Maps & Reports"
    OTHER = "Other"
    ANNUAL_AND_MONTHLY_REPORTS = "Annual & Monthly Reports"
    RESOURCES = "Resources"
    DISPATCH_LOGS = "Dispatch Logs"
    SEX_OFFENDER_REGISTRY = "Sex Offender Registry"
    OFFICER_INVOLVED_SHOOTINGS = "Officer Involved Shootings"
    DAILY_ACTIVITY_LOGS = "Daily Activity Logs"
    CRIME_STATISTICS = "Crime Statistics"
    RECORDS_REQUEST_INFO = "Records Request Info"
    POLICIES_AND_CONTRACTS = "Policies & Contracts"
    STOPS = "Stops"
    MEDIA_BULLETINS = "Media Bulletins"
    TRAINING_AND_HIRING_INFO = "Training & Hiring Info"
    PERSONNEL_RECORDS = "Personnel Records"
    CONTACT_INFO_AND_AGENCY_META = "Contact Info & Agency Meta"
    INCIDENT_REPORTS = "Incident Reports"
    CALLS_FOR_SERVICE = "Calls for Service"
    ACCIDENT_REPORTS = "Accident Reports"
    USE_OF_FORCE_REPORTS = "Use of Force Reports"
    COMPLAINTS_AND_MISCONDUCT = "Complaints & Misconduct"
    VEHICLE_PURSUITS = "Vehicle Pursuits"
    COURT_CASES = "Court Cases"
    SURVEYS = "Surveys"
    FIELD_CONTACTS = "Field Contacts"
    WANTED_PERSONS = "Wanted Persons"
    LIST_OF_DATA_SOURCES = "List of Data Sources"