import traceback
from http import HTTPStatus
from typing import Any

from fastapi import HTTPException

from db.client.core import DatabaseClient
from db.queries.builder.core import QueryBuilderBase


def run_query_builder(query_builder: QueryBuilderBase) -> Any:
    try:
        db_client = DatabaseClient()
        return db_client.run_query_builder(query_builder)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
