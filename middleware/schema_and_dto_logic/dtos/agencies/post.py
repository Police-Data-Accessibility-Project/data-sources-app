from typing import Optional

from pydantic import Field, BaseModel
from middleware.enums import JurisdictionType, AgencyType
from middleware.schema_and_dto_logic.dtos.agencies.base import AgencyInfoBaseDTO
from middleware.schema_and_dto_logic.dtos.agencies._helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class AgencyInfoPostDTO(AgencyInfoBaseDTO):
    name: str = get_name_field(required=True)
    jurisdiction_type: JurisdictionType = get_jurisdiction_type_field(required=True)
    agency_type: AgencyType = Field(
        description="The type of the agency.",
        json_schema_extra=MetadataInfo(required=True),
    )


class AgenciesPostDTO(BaseModel):
    agency_info: AgencyInfoPostDTO
    location_ids: Optional[list[int]] = None
