from typing import Optional

from pydantic import BaseModel

from endpoints.instantiations.source_collector.meta_urls.post.enums import (
    MetaURLCreationResponse,
)
from middleware.schema_and_dto.dtos._helpers import (
    default_field_not_required,
    default_field_required,
)


class SourceCollectorMetaURLPostResponseInnerDTO(BaseModel):
    url: Optional[str] = default_field_not_required(
        description="The URL of the created meta URL.",
    )
    agency_id: Optional[int] = default_field_not_required(
        description="The ID of the agency that the meta URL is associated with.",
    )
    status: MetaURLCreationResponse = default_field_required(
        description="The status of the meta URL creation.",
    )
    meta_url_id: Optional[int] = default_field_not_required(
        description="The ID of the created meta URL, if successful.",
    )
    error: Optional[str] = default_field_not_required(
        description="The error message, if the meta URL creation failed.",
    )


class SourceCollectorMetaURLPostResponseDTO(BaseModel):
    meta_urls: list[SourceCollectorMetaURLPostResponseInnerDTO] = (
        default_field_required(
            description="The list of meta URLs created.",
        )
    )
