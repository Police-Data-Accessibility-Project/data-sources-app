from typing import Literal

from sqlalchemy import Text, func, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, DATERANGE
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from sqlalchemy.dialects import postgresql

from database_client.enums import LocationType

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
ApprovalStatusLiteral = Literal[
    "rejected", "approved", "needs identification", "pending"
]
URLStatusLiteral = Literal["available", "none found", "ok", "broken"]
RetentionScheduleLiteral = Literal[
    "1-10 years",
    "< 1 week",
    "1 day",
    "Future only",
    "< 1 day",
    "< 1 year",
    "1 month",
    "1 week",
    "> 10 years",
]
DetailLevelLiteral = Literal[
    "Individual record", "Aggregated records", "Summarized totals"
]
AccessTypeLiteral = Literal["Web page", "API", "Download"]
UpdateMethodLiteral = Literal["Insert", "No updates", "Overwrite"]
RequestUrgencyLiteral = Literal[
    "urgent",
    "somewhat_urgent",
    "not_urgent",
    "long_term",
    "indefinite_unknown",
]
LocationTypeLiteral = Literal["State", "County", "Locality"]
LocationTypePGEnum = postgresql.ENUM(
    LocationType.STATE.value,
    LocationType.COUNTY.value,
    LocationType.LOCALITY.value,
    name="location_type",
)
EventTypeDataRequestLiteral = Literal["Request Ready to Start", "Request Complete"]
EventTypeDataSourceLiteral = Literal["Data Source Approved"]
EntityTypeLiteral = Literal["Data Request", "Data Source"]
AgencyAggregationLiteral = Literal["county", "local", "state", "federal"]
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
