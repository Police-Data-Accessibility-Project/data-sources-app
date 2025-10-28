from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.source_collector.agencies.search.locations.schema_config import (
    SourceCollectorAgencySearchLocationSchemaConfig,
)
from endpoints.instantiations.source_collector.agencies.search.locations.wrapper import (
    source_collector_search_agencies_by_location,
)
from endpoints.instantiations.source_collector.data_sources.duplicates.wrapper import (
    check_for_duplicate_urls,
)
from endpoints.instantiations.source_collector.data_sources.post.wrapper import (
    add_data_sources_from_source_collector,
)
from endpoints.instantiations.source_collector.meta_urls.post.endpoint_schema_config import (
    SourceCollectorMetaURLPostEndpointSchemaConfig,
)
from endpoints.instantiations.source_collector.meta_urls.post.wrapper import (
    add_meta_urls_from_source_collector,
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


@namespace_source_collector.route("/agencies/search/location", methods=["POST"])
class SourceCollectorAgenciesSearchLocation(PsycopgResource):
    @endpoint_info(
        namespace=namespace_source_collector,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES],
        ),
        schema_config=SchemaConfigs.SOURCE_COLLECTOR_SEARCH_AGENCIES_LOCATION,
        response_info=ResponseInfo(
            success_message="Successfully searched for agencies by location"
        ),
        description="Bulk submit multiple location objects and receive suggested agencies for each.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=source_collector_search_agencies_by_location,
            schema_populate_parameters=SourceCollectorAgencySearchLocationSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_source_collector.route("/meta-urls", methods=["POST"])
class SourceCollectorMetaURLs(PsycopgResource):
    @endpoint_info(
        namespace=namespace_source_collector,
        auth_info=AuthenticationInfo(
            allowed_access_methods=[AccessTypeEnum.JWT],
            restrict_to_permissions=[PermissionsEnum.SOURCE_COLLECTOR_DATA_SOURCES],
        ),
        schema_config=SchemaConfigs.SOURCE_COLLECTOR_META_URLS_POST,
        response_info=ResponseInfo(success_message="Successfully added meta urls"),
        description="Add meta URLs in bulk.",
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=add_meta_urls_from_source_collector,
            schema_populate_parameters=SourceCollectorMetaURLPostEndpointSchemaConfig.get_schema_populate_parameters(),
        )


