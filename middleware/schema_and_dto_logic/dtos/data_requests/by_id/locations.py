from pydantic import Field

from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetByIDBaseDTO
from middleware.schema_and_dto_logic.dynamic_logic.pydantic_to_marshmallow.core import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class RelatedLocationsByIDDTO(GetByIDBaseDTO):
    location_id: int = Field(
        description="The ID of the location to add or remove from the data request.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.PATH,
        ),
    )

    def get_where_mapping(self):
        return {
            "location_id": int(self.location_id),
            "data_request_id": int(self.resource_id),
        }
