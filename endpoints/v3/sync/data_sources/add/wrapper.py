from fastapi import HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.sync.data_sources.add.query import SourceManagerAddDataSourcesQueryBuilder
from endpoints.v3.sync.data_sources.add.request import AddDataSourcesOuterRequest
from endpoints.v3.sync.shared.models.response.add import SourceManagerSyncAddOuterResponse


def source_manager_add_data_sources(
    request: AddDataSourcesOuterRequest,
) -> SourceManagerSyncAddOuterResponse:
    try:
        db_client = DatabaseClient()
        return db_client.run_query_builder(SourceManagerAddDataSourcesQueryBuilder(request))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))