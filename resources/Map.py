from flask import Response

from middleware.access_logic import GET_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info_2
from middleware.primary_resource_logic.data_sources_logic import (
    get_data_sources_for_map_wrapper,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace

namespace_map = create_namespace(AppNamespaces.MAP)


@namespace_map.route("/data-sources")
class DataSourcesMap(PsycopgResource):
    """
    A resource for managing collections of data sources for mapping.
    Provides a method for retrieving all data sources.
    """

    @endpoint_info_2(
        namespace=namespace_map,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_MAP,
        response_info=ResponseInfo(
            success_message="Returns all requested data sources.",
        ),
        description="Retrieves location-relevant columns for data sources.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves location relevant columns for data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        return self.run_endpoint(get_data_sources_for_map_wrapper)
