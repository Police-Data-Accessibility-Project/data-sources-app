from datetime import datetime

from pydantic import BaseModel, Field

from db.enums import RequestStatus, RequestUrgency
from endpoints.instantiations.locations_._shared.dtos.response import (
    LocationInfoResponseDTO,
)
from middleware.enums import RecordTypesEnum


class GetDataSourceLimitedModel(BaseModel):
    class Config:
        frozen = True

    id: int = Field(
        description="The ID of the data source.",
    )
    name: str = Field(
        description="The name of the data source.",
    )


class GetDataRequestInfoModel(BaseModel):
    id: int = Field(
        description="The ID of the data request.",
    )
    title: str = Field(
        description="The title of the data request.",
    )
    submission_notes: str | None = Field(
        description="The submission notes of the data request.",
    )
    request_status: RequestStatus = Field(
        description="The status of the data request.",
    )
    archive_reason: str | None = Field(
        description="The reason for archiving the data request.",
    )
    date_created: datetime = Field(
        description="The date the data request was created.",
    )
    date_status_last_changed: datetime = Field(
        description="The date the status of the data request was last changed.",
    )
    creator_user_id: int = Field(
        description="The ID of the user who created the data request.",
    )
    github_issue_url: str | None = Field(
        description="The URL of the GitHub issue associated with the data request.",
    )
    github_issue_number: int | None = Field(
        description="The number of the GitHub issue associated with the data request.",
    )
    internal_notes: str | None = Field(
        description="The internal notes of the data request.",
    )
    record_types_required: list[RecordTypesEnum] = Field(
        description="The record types required for the data request.",
    )
    pdap_response: str | None = Field(
        description="The PDAP response of the data request.",
    )
    coverage_range: str | None = Field(
        description="The coverage range of the data request.",
    )
    data_requirements: str | None = Field(
        description="The data requirements of the data request.",
    )
    request_urgency: RequestUrgency = Field(
        description="The urgency of the data request.",
    )


class GetUserDataRequestModel(BaseModel):
    info: GetDataRequestInfoModel = Field(
        description="The info of the data request.",
    )
    data_sources: list[GetDataSourceLimitedModel] = Field(
        description="The data sources associated with the data request.",
    )
    data_source_ids: list[int] = Field(
        description="The data source ids associated with the data request.",
    )
    locations: list[LocationInfoResponseDTO] = Field(
        description="The locations associated with the data request",
    )
    location_ids: list[int] = Field(
        description="The location ids associated with the data request",
    )
