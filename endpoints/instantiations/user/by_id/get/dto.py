from pydantic import BaseModel

from middleware.schema_and_dto.dtos._helpers import default_field_required


class ExternalAccountDTO(BaseModel):
    github: str = default_field_required(description="The GitHub user id of the user")