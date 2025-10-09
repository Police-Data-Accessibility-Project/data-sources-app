from typing import Optional

from pydantic import BaseModel

from middleware.enums import RecordTypes, JurisdictionType
from middleware.schema_and_dto.dtos._helpers import default_field_required


class SearchResultDTO(BaseModel):
    id: int = default_field_required("The ID of the search result.")
    agency_name: str = default_field_required("The name of the agency.")
    municipality: str = default_field_required("The municipality of the agency.")
    state_iso: str = default_field_required("The state iso of the agency.")
    data_source_name: str = default_field_required("The name of the data source.")
    description: Optional[str] = default_field_required("The description of the data source.")
    record_type: RecordTypes = default_field_required("The type of the record.")
    source_url: Optional[str] = default_field_required("The URL of the source.")
    record_formats: Optional[list[str]] = default_field_required("The formats of the record.")
    coverage_start: Optional[str] = default_field_required("The start of the coverage.")
    coverage_end: Optional[str] = default_field_required("The end of the coverage.")
    agency_supplied: bool = default_field_required("Whether the agency supplied the data.")
    jurisdiction_type: JurisdictionType = default_field_required("The type of the jurisdiction.")


class SearchResponseInnerDTO(BaseModel):
    results: list[SearchResultDTO] = default_field_required("The list of search results.")
    count: int = default_field_required("The count of the search results.")

class SearchResponseJurisdictionsWrapperDTO(BaseModel):
    federal: SearchResponseInnerDTO= default_field_required("The list of federal search results.")
    state: SearchResponseInnerDTO = default_field_required("The list of state search results.")
    county: SearchResponseInnerDTO = default_field_required("The list of county search results.")
    locality: SearchResponseInnerDTO = default_field_required("The list of city search results.")

class SearchResponseDTO(BaseModel):
    data: SearchResponseJurisdictionsWrapperDTO = default_field_required("The list of search results.")
    count: int = default_field_required("The count of the search results.")