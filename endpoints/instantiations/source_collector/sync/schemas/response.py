from endpoints.instantiations.source_collector.sync.dtos.response import (
    SourceCollectorSyncAgenciesResponseOuterDTO,
)
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import (
    pydantic_to_marshmallow,
)

SourceCollectorSyncAgenciesResponseSchema = pydantic_to_marshmallow(
    SourceCollectorSyncAgenciesResponseOuterDTO
)
