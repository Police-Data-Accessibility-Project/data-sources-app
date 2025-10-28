from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.sync.agencies.add.query import SourceManagerAddAgenciesQueryBuilder
from endpoints.v3.sync.agencies.add.request import AddAgenciesOuterRequest
from endpoints.v3.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)


def source_manager_add_agencies(
    request: AddAgenciesOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    try:
        db_client = DatabaseClient()
        return db_client.run_query_builder(
            SourceManagerAddAgenciesQueryBuilder(request)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
