from typing import Optional

from pydantic import BaseModel, Field

from db.enums import RequestUrgency, RequestStatus
from middleware.enums import RecordTypes
from middleware.schema_and_dto.dtos._helpers import default_field_not_required, default_field_required
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo


class RequestInfoPostDTO(BaseModel):
    title: str = Field(
        description="The title of the data request.",
        json_schema_extra=MetadataInfo(required=True),
        min_length=1,
        max_length=255
    )
    submission_notes: str = default_field_required(
        description="Optional notes provided by the submitter during the request submission."
    )
    request_urgency: RequestUrgency = default_field_required(
        description="The urgency of the data request."
    )
    coverage_range: Optional[str] = default_field_not_required(
        description="The coverage range of the data request."
    )
    data_requirements: Optional[str] = default_field_not_required(
        description="The data requirements of the data request."
    )
    record_types_required: Optional[list[RecordTypes]] = default_field_not_required(
        description="The record types required for the data request."
    )
    request_status: RequestStatus = Field(
        default=RequestStatus.INTAKE,
        description="The status of the data request.",
        json_schema_extra=MetadataInfo(required=False),
    )




class DataRequestsPostDTO(BaseModel):
    request_info: RequestInfoPostDTO = default_field_required(
        description="The information about the data request to be created"
    )
    location_ids: Optional[list[int]] = default_field_not_required(
        description="The location ids associated with the data request"
    )
