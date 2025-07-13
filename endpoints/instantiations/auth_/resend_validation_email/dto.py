from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class EmailOnlyDTO(BaseModel):
    email: str = default_field_required(description="The user's email address",)
