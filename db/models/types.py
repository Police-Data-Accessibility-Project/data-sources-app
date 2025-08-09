from typing import Literal

from sqlalchemy import Text, func, String, Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP, DATERANGE
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from sqlalchemy.dialects import postgresql

from db.enums import LocationType
from middleware.enums import JurisdictionType

ExternalAccountTypeLiteral = Literal["github"]
RecordTypeLiteral = Literal[
    "Dispatch Recordings",
    "Arrest Records",
    "Citations",
    "Incarceration Records",
    "Booking Reports",
    "Budgets & Finances",
    "Misc Police Activity",
    "Geographic",
    "Crime Maps & Reports",
    "Other",
    "Annual & Monthly Reports",
    "Resources",
    "Dispatch Logs",
    "Sex Offender Registry",
    "Officer Involved Shootings",
    "Daily Activity Logs",
    "Crime Statistics",
    "Records Request Info",
    "Policies & Contracts",
    "Stops",
    "Media Bulletins",
    "Training & Hiring Info",
    "Personnel Records",
    "Contact Info & Agency Meta",
    "Incident Reports",
    "Calls for Service",
    "Accident Reports",
    "Use of Force Reports",
    "Complaints & Misconduct",
    "Vehicle Pursuits",
    "Court Cases",
    "Surveys",
    "Field Contacts",
    "Wanted Persons",
    "List of Data Sources",
    "Car GPS",
]
RequestStatusLiteral = Literal[
    "Intake",
    "Active",
    "Complete",
    "Request withdrawn",
    "Waiting for scraper",
    "Archived",
    "Ready to start",
    "Waiting for FOIA",
    "Waiting for requestor",
]
OperationTypeLiteral = Literal["UPDATE", "DELETE", "INSERT"]
JurisdictionTypeLiteral = Literal[
    "federal", "state", "county", "local", "port", "tribal", "transit", "school"
]
JurisdictionTypeEnum = Enum(
    JurisdictionType,
    name="jurisdiction_type",
)
ApprovalStatusLiteral = Literal[
    "rejected", "approved", "needs identification", "pending"
]
URLStatusLiteral = Literal["ok", "broken"]

AccessTypeLiteral = Literal["Web page", "API", "Download"]
RequestUrgencyLiteral = Literal[
    "urgent",
    "somewhat_urgent",
    "not_urgent",
    "long_term",
    "indefinite_unknown",
]
LocationTypeLiteral = Literal["State", "County", "Locality", "National"]
LocationTypePGEnum = postgresql.ENUM(
    LocationType.STATE.value,
    LocationType.COUNTY.value,
    LocationType.LOCALITY.value,
    LocationType.NATIONAL.value,
    name="location_type",
)
EventTypeDataRequestLiteral = Literal["Request Ready to Start", "Request Complete"]
EventTypeDataSourceLiteral = Literal["Data Source Approved"]
AgencyTypeLiteral = Literal[
    "incarceration",
    "law enforcement",
    "aggregated",
    "court",
    "unknown",
]
text = Annotated[Text, None]
timestamp_tz = Annotated[
    TIMESTAMP, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
]
timestamp = Annotated[TIMESTAMP, None]
daterange = Annotated[DATERANGE, None]
str_255 = Annotated[String, 255]
