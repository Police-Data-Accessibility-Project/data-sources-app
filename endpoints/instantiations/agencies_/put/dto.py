from typing import Optional

from pydantic import Field, BaseModel

from db.enums import ApprovalStatus
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto.dtos.agencies._helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class AgencyInfoPutDTO(BaseModel):
    name: str = get_name_field(required=False)
    jurisdiction_type: JurisdictionType = get_jurisdiction_type_field(required=False)
    agency_type: Optional[AgencyType] = Field(
        default=None,
        description="The type of the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    multi_agency: bool = Field(
        default=False,
        description="Whether or not the agency is a multi-agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    no_web_presence: bool = Field(
        default=False,
        description="Whether or not the agency has no web presence.",
        json_schema_extra=MetadataInfo(required=False),
    )
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING,
        description="The approval status of the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    meta_urls: list[str] = Field(
        default=[],
        description="The meta URLs of the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    defunct_year: Optional[str] = Field(
        default=None,
        description="If present, denotes an agency which has defunct but may still have relevant records.",
        json_schema_extra=MetadataInfo(required=False),
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        description="If present, denotes a rejection reason for an agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    last_approval_editor: Optional[str] = Field(
        default=None,
        description="The user who last approved the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
    submitter_contact: Optional[str] = Field(
        default=None,
        description="The contact information of the user who submitted the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
