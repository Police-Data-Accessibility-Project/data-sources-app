from pydantic import BaseModel, Field

from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class TypeaheadDTO(BaseModel):
    query: str = Field(
        description="The search query to get suggestions for.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.QUERY_ARGS, required=True
        ),
    )
