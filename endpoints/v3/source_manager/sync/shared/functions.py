from fastapi import HTTPException

from db.client.core import DatabaseClient
from db.client.helpers import run_query_builder
from db.queries.builder.core import QueryBuilderBase
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def run_sync_query_builder(query_builder: QueryBuilderBase) -> MessageDTO:
    run_query_builder(query_builder)
    return MessageDTO(message="Sync completed successfully")
