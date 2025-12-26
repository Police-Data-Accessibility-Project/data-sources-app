from fastapi import APIRouter, Depends

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.data_sources.duplicate.request import SourceManagerDataSourcesDuplicateRequest
from endpoints.v3.source_manager.data_sources.duplicate.response import SourceManagerDataSourcesDuplicateResponse
from endpoints.v3.source_manager.data_sources.duplicate.wrapper import check_for_duplicate_urls
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.fastapi import get_source_collector_data_sources_access_info

data_sources_router = APIRouter(prefix="/data-sources", tags=["Data Sources"])

@data_sources_router.post(
    "/duplicates",
)
def check_for_data_source_duplicates(
    request: SourceManagerDataSourcesDuplicateRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> SourceManagerDataSourcesDuplicateResponse:
    return check_for_duplicate_urls(
        db_client=DatabaseClient(),
        request=request,
    )

# Meta URLs
