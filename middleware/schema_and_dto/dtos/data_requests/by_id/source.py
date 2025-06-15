from pydantic import Field

from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.generator.models.metadata import (
    MetadataInfo,
)
from utilities.enums import SourceMappingEnum


class RelatedSourceByIDDTO(GetByIDBaseDTO):
    data_source_id: int = Field(
        description="The ID of the data source to retrieve.",
        json_schema_extra=MetadataInfo(
            source=SourceMappingEnum.PATH,
        ),
    )

    def get_where_mapping(self):
        return {
            "data_source_id": int(self.data_source_id),
            "request_id": int(self.resource_id),
        }
