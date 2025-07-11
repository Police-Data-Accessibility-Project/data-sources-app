from pydantic import BaseModel

from middleware.schema_and_dto.non_dto_dataclasses import DTOPopulateParameters
from middleware.schema_and_dto.schemas.data_sources.entry_data_request import EntryDataRequestSchema
from utilities.enums import SourceMappingEnum


class EntryCreateUpdateRequestDTO(BaseModel):
    """
    Contains data for creating or updating an entry
    """

    entry_data: dict

    @classmethod
    def get_dto_populate_parameters(cls) -> DTOPopulateParameters:
        return DTOPopulateParameters(
            dto_class=EntryCreateUpdateRequestDTO,
            source=SourceMappingEnum.JSON,
            validation_schema=EntryDataRequestSchema,
        )
