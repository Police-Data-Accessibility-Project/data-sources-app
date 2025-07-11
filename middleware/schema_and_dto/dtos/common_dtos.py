from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class MessageDTO(BaseModel):
    message: str = default_field_required(description="A message returned in the response")

class IDAndMessageDTO(MessageDTO):
    id: str = default_field_required(description="The id of the created entry")

class GetManyResponseDTOBase(MessageDTO):
    metadata: dict = default_field_required(description="Metadata of the results")

class GetManyResponseDTO(GetManyResponseDTOBase):
    data: list[dict] = default_field_required(description="The list of results")