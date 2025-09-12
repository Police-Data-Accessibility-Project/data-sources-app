# pyright: reportUnknownVariableType = false
import datetime
from typing import Optional

from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import (
    default_field_required,
    default_field_not_required,
)


class SourceCollectorSyncAgenciesResponseInnerDTO(BaseModel):
    display_name: str = default_field_required(
        description="The display name of the agency."
    )
    agency_id: int = default_field_required(description="The id of the agency.")
    state_name: Optional[str] = default_field_not_required(
        description="The state name of the agency."
    )
    county_name: Optional[str] = default_field_not_required(
        description="The county name of the agency."
    )
    locality_name: Optional[str] = default_field_not_required(
        description="The locality name of the agency."
    )
    meta_urls: list[str] = default_field_required(
        description="The meta URLs of the agency."
    )
    updated_at: datetime.datetime = default_field_required(
        description="The date and time the agency was last updated."
    )


class SourceCollectorSyncAgenciesResponseOuterDTO(BaseModel):
    agencies: list[SourceCollectorSyncAgenciesResponseInnerDTO] = (
        default_field_required("Agency information included in the sync.")
    )
