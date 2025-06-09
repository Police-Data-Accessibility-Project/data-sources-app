from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)


class LocationPutDTO(BaseModel):
    latitude: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
    longitude: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
