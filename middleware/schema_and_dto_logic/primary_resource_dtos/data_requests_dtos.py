from dataclasses import dataclass
from typing import Optional

from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType, RequestStatus, RequestUrgency
from middleware.enums import RecordType
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


@dataclass
class DataRequestLocationInfoPostDTO:
    type: LocationType
    state: str
    county: Optional[str] = None
    locality: Optional[str] = None

    def get_where_mappings(self) -> list[WhereMapping]:
        d =  {
            "type": self.type,
            "state": self.state,
        }
        if self.county is not None:
            d["county"] = self.county
        if self.locality is not None:
            d["locality"] = self.locality
        return WhereMapping.from_dict(d)

@dataclass
class GetManyDataRequestsRequestsDTO(GetManyBaseDTO):
    request_status: Optional[RequestStatus] = None


@dataclass
class DataRequestsPutDTO:
    title: Optional[str] = None
    submission_notes: Optional[str] = None
    request_urgency: Optional[RequestUrgency] = None
    coverage_range: Optional[str] = None
    data_requirements: Optional[str] = None
    request_status: Optional[RequestStatus] = None
    archive_reason: Optional[str] = None
    github_issue_url: Optional[str] = None
    github_issue_number: Optional[int] = None
    internal_notes: Optional[str] = None
    record_types_required: Optional[list[RecordType]] = None
    pdap_response: Optional[str] = None


@dataclass
class DataRequestsPutOuterDTO:
    entry_data: DataRequestsPutDTO
