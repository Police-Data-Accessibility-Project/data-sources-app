from typing import Any

from db.queries.helpers import run_query_builder
from db.queries.builder.core import QueryBuilderBase
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def run_sync_query_builder(query_builder: QueryBuilderBase) -> Any:
    result = run_query_builder(query_builder)
    if result is not None:
        return result
    return MessageDTO(message="Sync completed successfully")
