from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.source_collector.data_sources.duplicates.wrapper import (
    check_for_duplicate_urls,
)
from endpoints.instantiations.source_collector.data_sources.post.wrapper import (
    add_data_sources_from_source_collector,
)
from endpoints.instantiations.source_collector.sync.middleware.wrapper import (
    get_agencies_for_sync,
)
from endpoints.instantiations.source_collector.sync.schema_config import (
    SourceCollectorSyncAgenciesSchemaConfig,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.source_collector.data_sources import (
    SourceCollectorDataSourcesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.source_collector.duplicates import (
    SourceCollectorDuplicatesPostEndpointSchemaConfig,
)
from middleware.decorators.endpoint_info import endpoint_info
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.base import AuthenticationInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_source_collector = create_namespace(AppNamespaces.SOURCE_COLLECTOR)


@namespace_source_collector.route("/data-sources", methods=["POST"])
class SourceCollectorDataSources(PsycopgResource):

    @endpoint_info(
        namespace=namespace_source_collector,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES],
        ),
        schema_config=SchemaConfigs.SOURCE_COLLECTOR_DATA_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Data sources successfully updated."
        ),
        description="Adds data sources from the source collector in bulk.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=add_data_sources_from_source_collector,
            schema_populate_parameters=SourceCollectorDataSourcesPostEndpointSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_source_collector.route("/data-sources/duplicates", methods=["POST"])
class SourceCollectorDataSourcesDuplicates(PsycopgResource):

    @endpoint_info(
        namespace=namespace_source_collector,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES],
        ),
        schema_config=SchemaConfigs.SOURCE_COLLECTOR_DUPLICATES_POST,
        response_info=ResponseInfo(
            success_message="Successfully checks for duplicate URLs"
        ),
        description="Checks for duplicate URLs in Bulk.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=check_for_duplicate_urls,
            schema_populate_parameters=SourceCollectorDuplicatesPostEndpointSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_source_collector.route("/agencies/sync", methods=["GET"])
class SourceCollectorSyncAgencies(PsycopgResource):

    @endpoint_info(
        namespace=namespace_source_collector,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES],
        ),
        schema_config=SchemaConfigs.SOURCE_COLLECTOR_SYNC_AGENCIES,
        response_info=ResponseInfo(
            success_message="Successfully returns agencies to sync"
        ),
        description="Syncs agencies.",
    )
    def get(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=get_agencies_for_sync,
            schema_populate_parameters=SourceCollectorSyncAgenciesSchemaConfig.get_schema_populate_parameters(),
        )
