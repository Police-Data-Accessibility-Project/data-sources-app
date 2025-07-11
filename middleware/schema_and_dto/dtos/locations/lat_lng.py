from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)


class LatLngDTO(BaseModel):
    lat: Optional[float] = Field(
        default=None,
        description="The latitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
    lng: Optional[float] = Field(
        default=None,
        description="The longitude of the location",
        json_schema_extra=MetadataInfo(required=False),
    )
