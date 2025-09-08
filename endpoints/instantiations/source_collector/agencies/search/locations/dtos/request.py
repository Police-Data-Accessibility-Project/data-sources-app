from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class SourceCollectorAgencySearchLocationRequestInnerDTO(BaseModel):
    query: str = default_field_required(
        description="The query to search for agencies by location.",
    )
    request_id: int = default_field_required(
        description="The request ID, used in identifying the response",
    )

class SourceCollectorAgencySearchLocationRequestDTO(BaseModel):
    requests: list[SourceCollectorAgencySearchLocationRequestInnerDTO] = default_field_required(
        description="The list of requests to search for agencies by location.",
    )