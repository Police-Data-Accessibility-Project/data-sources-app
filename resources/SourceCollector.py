from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import AuthenticationInfo
from middleware.decorators import endpoint_info
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.primary_resource_logic.source_collector_logic import (
    add_data_sources_from_source_collector,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_source_collector = create_namespace(AppNamespaces.SOURCE_COLLECTOR)


@namespace_source_collector.route("/data_sources", methods=["POST"])
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
            schema_populate_parameters=SchemaConfigs.SOURCE_COLLECTOR_DATA_SOURCES_POST.value.get_schema_populate_parameters(),
        )
