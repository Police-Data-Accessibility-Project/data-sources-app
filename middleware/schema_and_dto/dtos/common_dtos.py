from pydantic import BaseModel, Field

from middleware.schema_and_dto.dtos._helpers import default_field_required, default_field_not_required
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import MetadataInfo


class MessageDTO(BaseModel):
    message: str = Field(
        default="",
        description="A message returned in the response",
        json_schema_extra=MetadataInfo(required=False),
    )

class IDAndMessageDTO(MessageDTO):
    id: str = default_field_required(description="The id of the created entry")

class GetManyResponseDTOBase(MessageDTO):
    metadata: dict = default_field_required(description="Metadata of the results")

class GetManyResponseDTO(GetManyResponseDTOBase):
    data: list[dict] = default_field_required(description="The list of results")