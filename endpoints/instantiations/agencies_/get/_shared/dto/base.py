from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from endpoints.instantiations.locations_._shared.dtos.response import (
    LocationInfoResponseDTO,
)
from middleware.enums import JurisdictionType
from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)
from middleware.schema_and_dto.dtos.agencies.base import AgencyInfoBaseDTO


class DataSourcesSmallDTO(BaseModel):
    id: int = default_field_required(description="The id of the data source.")
    name: str = default_field_required(description="The name of the data source.")


class AgenciesGetDTO(AgencyInfoBaseDTO):
    class Config:
        arbitrary_types_allowed = True

    id: int = default_field_required(
        description="The id of the agency.",
    )
    meta_urls: list[str] = default_field_required(
        description="The meta URLs of the agency.",
    )
    submitted_name: str = default_field_required(
        description="The submitted name of the agency.",
    )
    jurisdiction_type: JurisdictionType = default_field_required(
        description="The jurisdiction type of the agency.",
    )
    name: Optional[str] = default_field_not_required(
        description="The name of the agency.",
    )
    state_iso: Optional[str] = default_field_not_required(
        description="The ISO code of the state in which the agency is located. Does not apply to federal agencies.",
    )
    state_name: Optional[str] = default_field_not_required(
        description="The name of the state in which the agency is located. Does not apply to federal agencies.",
    )
    county_name: Optional[str] = default_field_not_required(
        description="The name of the county in which the agency is located. Does not apply to federal agencies.",
    )
    county_fips: Optional[str] = default_field_not_required(
        description="The FIPS code of the county in which the agency is located. Does not apply to federal agencies.",
    )
    locality_name: Optional[str] = default_field_not_required(
        description="The name of the locality in which the agency is located. Does not apply to federal agencies.",
    )
    airtable_agency_last_modified: datetime = default_field_not_required(
        description="The date and time the agency was last updated.",
    )
    agency_created: datetime = default_field_not_required(
        description="The date and time the agency was created.",
    )
    data_sources: list[DataSourcesSmallDTO] = default_field_required(
        description="The data sources associated with the agency.",
    )
    locations: list[LocationInfoResponseDTO] = default_field_required(
        description="The locations associated with the agency.",
    )
