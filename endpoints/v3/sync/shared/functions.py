from fastapi import HTTPException

from db.client.core import DatabaseClient
from db.queries.builder.core import QueryBuilderBase
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO


def run_sync_query_builder(query_builder: QueryBuilderBase) -> MessageDTO:
    try:
        db_client = DatabaseClient()
        db_client.run_query_builder(query_builder)
        return MessageDTO(message="Sync completed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
