from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class MessageDTO(BaseModel):
    message: str = default_field_required(description="A message returned in the response")

class IDAndMessageDTO(BaseModel):
    id: str = default_field_required(description="The id of the created entry")
