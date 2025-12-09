from fastapi import APIRouter, Depends, HTTPException

from db.client.core import DatabaseClient
from endpoints.v3.source_manager.follows.query import (
    GetUserFollowsSourceCollectorQueryBuilder,
)
from endpoints.v3.source_manager.follows.response import GetFollowsResponse
from endpoints.v3.source_manager.sync.agencies.add.request import (
    AddAgenciesOuterRequest,
)
from endpoints.v3.source_manager.sync.agencies.add.wrapper import (
    source_manager_add_agencies,
)
from endpoints.v3.source_manager.sync.agencies.delete.exceptions import (
    OrphanedEntityException,
)
from endpoints.v3.source_manager.sync.agencies.delete.wrapper import (
    source_manager_delete_agencies,
)
from endpoints.v3.source_manager.sync.agencies.update.request import (
    UpdateAgenciesOuterRequest,
)
from endpoints.v3.source_manager.sync.agencies.update.wrapper import (
    source_manager_update_agencies,
)
from endpoints.v3.source_manager.sync.data_sources.add.request import (
    AddDataSourcesOuterRequest,
)
from endpoints.v3.source_manager.sync.data_sources.add.wrapper import (
    source_manager_add_data_sources,
)
from endpoints.v3.source_manager.sync.data_sources.delete.wrapper import (
    source_manager_delete_data_sources,
)
from endpoints.v3.source_manager.sync.data_sources.update.request import (
    UpdateDataSourcesOuterRequest,
)
from endpoints.v3.source_manager.sync.data_sources.update.wrapper import (
    source_manager_update_data_sources,
)
from endpoints.v3.source_manager.sync.meta_urls.add.request import (
    AddMetaURLsOuterRequest,
)
from endpoints.v3.source_manager.sync.meta_urls.add.wrapper import (
    source_manager_add_meta_urls,
)
from endpoints.v3.source_manager.sync.meta_urls.delete.wrapper import (
    source_manager_delete_meta_urls,
)
from endpoints.v3.source_manager.sync.meta_urls.update.request import (
    UpdateMetaURLsOuterRequest,
)
from endpoints.v3.source_manager.sync.meta_urls.update.wrapper import (
    source_manager_update_meta_urls,
)
from endpoints.v3.source_manager.sync.shared.models.request.delete import (
    SourceManagerDeleteRequest,
)
from endpoints.v3.source_manager.sync.shared.models.response.add import (
    SourceManagerSyncAddOuterResponse,
)
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.fastapi import (
    get_source_collector_data_sources_access_info,
)

sm_router = APIRouter(prefix="/sync", tags=["Sync"])


@sm_router.get("/follows")
def get_follows(
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> GetFollowsResponse:
    return DatabaseClient().run_query_builder(
        GetUserFollowsSourceCollectorQueryBuilder()
    )


# Data Sources
@sm_router.post("/data-sources/add")
def add_data_sources(
    request: AddDataSourcesOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> SourceManagerSyncAddOuterResponse:
    return source_manager_add_data_sources(request)


@sm_router.post("/data-sources/delete")
def delete_data_sources(
    request: SourceManagerDeleteRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    return source_manager_delete_data_sources(request)


@sm_router.post("/data-sources/update", response_model_exclude_unset=True)
def update_data_sources(
    request: UpdateDataSourcesOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    return source_manager_update_data_sources(request)


# Meta URLs


@sm_router.post("/meta-urls/add")
def add_meta_urls(
    request: AddMetaURLsOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> SourceManagerSyncAddOuterResponse:
    return source_manager_add_meta_urls(request)


@sm_router.post("/meta-urls/delete")
def delete_meta_urls(
    request: SourceManagerDeleteRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    return source_manager_delete_meta_urls(request)


@sm_router.post("/meta-urls/update", response_model_exclude_unset=True)
def update_meta_urls(
    request: UpdateMetaURLsOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    return source_manager_update_meta_urls(request)


# Agencies


@sm_router.post("/agencies/add")
def add_agencies(
    request: AddAgenciesOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> SourceManagerSyncAddOuterResponse:
    return source_manager_add_agencies(request)


@sm_router.post("/agencies/delete")
def delete_agencies(
    request: SourceManagerDeleteRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    try:
        return source_manager_delete_agencies(request)
    except OrphanedEntityException as e:
        raise HTTPException(status_code=400, detail=str(e))


@sm_router.post("/agencies/update", response_model_exclude_unset=True)
def update_agencies(
    request: UpdateAgenciesOuterRequest,
    access_info: AccessInfoPrimary = Depends(
        get_source_collector_data_sources_access_info
    ),
) -> MessageDTO:
    return source_manager_update_agencies(request)
