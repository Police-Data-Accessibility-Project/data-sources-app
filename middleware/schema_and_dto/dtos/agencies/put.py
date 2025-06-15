from typing import Optional

from pydantic import Field

from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto.dtos.agencies._helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from middleware.schema_and_dto.dtos.agencies.base import AgencyInfoBaseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class AgencyInfoPutDTO(AgencyInfoBaseDTO):
    name: str = get_name_field(required=False)
    jurisdiction_type: JurisdictionType = get_jurisdiction_type_field(required=False)
    agency_type: Optional[AgencyType] = Field(
        default=None,
        description="The type of the agency.",
        json_schema_extra=MetadataInfo(required=False),
    )
