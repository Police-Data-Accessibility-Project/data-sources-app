# pyright: reportUnknownVariableType = false
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from db.enums import URLStatus, ApprovalStatus
from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_required


class SourceCollectorSyncDataSourcesResponseInnerDTO(BaseModel):
    id: int = default_field_required(description="The id of the data source.")
    url: str = default_field_required(description="The url of the data source.")
    name: str = default_field_required(description="The name of the data source.")
    description: Optional[str] = default_field_required(
        description="The description of the data source."
    )
    record_type: RecordTypes = default_field_required(
        description="The record type of the data source."
    )
    agency_ids: list[int] = default_field_required(
        description="The ids of the agencies that supply the data source."
    )
    approval_status: ApprovalStatus = default_field_required(
        description="The approval status of the data source."
    )
    url_status: URLStatus = default_field_required(
        description="The URL status of the data source."
    )
    updated_at: datetime = default_field_required(
        description="The date and time the data source was last updated."
    )


class SourceCollectorSyncDataSourcesResponseDTO(BaseModel):
    data_sources: list[SourceCollectorSyncDataSourcesResponseInnerDTO] = (
        default_field_required(description="Data sources included in the sync.")
    )
