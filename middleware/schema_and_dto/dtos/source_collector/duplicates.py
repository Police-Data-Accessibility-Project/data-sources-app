from pydantic import BaseModel


class SourceCollectorDuplicatesPostRequestDTO(BaseModel):
    urls: list[str]
