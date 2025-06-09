from typing import Optional

from pydantic import BaseModel, Field

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
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
