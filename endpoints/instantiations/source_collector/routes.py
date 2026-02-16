from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.source_collector.agencies.search.locations.schema_config import (
    SourceCollectorAgencySearchLocationSchemaConfig,
)
from endpoints.instantiations.source_collector.agencies.search.locations.wrapper import (
    source_collector_search_agencies_by_location,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs

from middleware.decorators.endpoint_info import endpoint_info
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.base import AuthenticationInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_source_collector = create_namespace(AppNamespaces.SOURCE_COLLECTOR)


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
