from typing import Optional

from pydantic import BaseModel

from database_client.db_client_dataclasses import WhereMapping
from database_client.enums import LocationType, RequestStatus, RequestUrgency
from middleware.enums import RecordTypes
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetManyBaseDTO,
    GetByIDBaseDTO,
)


class DataRequestLocationInfoPostDTO(BaseModel):
    type: LocationType
    state_name: str
    county_name: Optional[str] = None
    locality_name: Optional[str] = None

    def get_where_mappings(self) -> list[WhereMapping]:
        d = {
            "type": self.type,
            "state": self.state_name,
        }
        if self.county_name is not None:
            d["county"] = self.county_name
        if self.locality_name is not None:
            d["locality"] = self.locality_name
        return WhereMapping.from_dict(d)


class GetManyDataRequestsRequestsDTO(GetManyBaseDTO):
    request_statuses: Optional[list[RequestStatus]] = None


class DataRequestsPutDTO(BaseModel):
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
    record_types_required: Optional[list[RecordTypes]] = None
    pdap_response: Optional[str] = None


class DataRequestsPutOuterDTO(BaseModel):
    entry_data: DataRequestsPutDTO


class RelatedSourceByIDDTO(GetByIDBaseDTO):
    data_source_id: int

    def get_where_mapping(self):
        return {
            "data_source_id": int(self.data_source_id),
            "request_id": int(self.resource_id),
        }


class RelatedLocationsByIDDTO(GetByIDBaseDTO):
    location_id: int

    def get_where_mapping(self):
        return {
            "location_id": int(self.location_id),
            "data_request_id": int(self.resource_id),
        }


class RequestInfoPostDTO(BaseModel):
    title: str
    submission_notes: str
    request_urgency: RequestUrgency
    coverage_range: Optional[str] = None
    data_requirements: Optional[str] = None


class DataRequestsPostDTO(BaseModel):
    request_info: RequestInfoPostDTO
    location_ids: Optional[list[int]] = None
