from pydantic import BaseModel

from middleware.schema_and_dto_logic.dtos.data_sources.base import (
    DataSourceEntryBaseDTO,
)


class DataSourceEntryDataPutDTO(DataSourceEntryBaseDTO): ...


class DataSourcesPutDTO(BaseModel):
    entry_data: DataSourceEntryDataPutDTO
