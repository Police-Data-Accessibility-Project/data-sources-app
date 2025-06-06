from typing import Optional

from pydantic import BaseModel, Field

from db.enums import LocationType
from middleware.enums import AgencyType
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class AgencyMatchRequestDTO(BaseModel):
    name: str = Field(
        description="The name of the agency to match.",
    )
    state: Optional[str] = Field(
        default=None,
        description="The state of the agency to match.",
        json_schema_extra=MetadataInfo(required=False),
    )
    county: Optional[str] = Field(
        default=None,
        description="The county of the agency to match.",
        json_schema_extra=MetadataInfo(required=False),
    )
    locality: Optional[str] = Field(
        default=None,
        description="The locality of the agency to match.",
        json_schema_extra=MetadataInfo(required=False),
    )

    def has_location_data(self) -> bool:
        return (
            self.state is not None
            or self.county is not None
            or self.locality is not None
        )


class AgencyMatchResponseLocationDTO(BaseModel):
    state: Optional[str]
    county: Optional[str]
    locality: Optional[str]
    location_type: Optional[LocationType]


class AgencyMatchResponseInnerDTO(BaseModel):
    id: int
    name: str
    agency_type: AgencyType
    locations: list[AgencyMatchResponseLocationDTO]
    similarity: float


class AgencyMatchResponseOuterDTO(BaseModel):
    entries: list[AgencyMatchResponseInnerDTO]
