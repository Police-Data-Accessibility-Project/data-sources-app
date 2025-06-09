from flask import Response

from config import limiter
from middleware.access_logic import AccessInfoPrimary
from middleware.authentication_info import API_OR_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.data_sources import (
    get_data_sources_for_map_wrapper,
)
from middleware.primary_resource_logic.locations import (
    get_locations_for_map_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import AppNamespaces, create_namespace

namespace_map = create_namespace(AppNamespaces.MAP)


@namespace_map.route("/data-sources")
class DataSourcesMap(PsycopgResource):
    """
    A resource for managing collections of data sources for mapping.
    Provides a method for retrieving all data sources.
    """

    @endpoint_info(
        namespace=namespace_map,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_MAP,
        response_info=ResponseInfo(
            success_message="Returns all requested data sources.",
        ),
        description="Retrieves location-relevant columns for data sources.",
    )
    @limiter.exempt
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves location relevant columns for data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        return self.run_endpoint(get_data_sources_for_map_wrapper)


@namespace_map.route("/locations")
class LocationsMap(PsycopgResource):
    """
    A resource for managing collections of data sources for mapping.
    Provides a method for retrieving all data sources.
    """

    @endpoint_info(
        namespace=namespace_map,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.LOCATIONS_MAP,
        response_info=ResponseInfo(
            success_message="Returns all requested locations.",
        ),
        description="Retrieves location-relevant columns for locations.",
    )
    @limiter.exempt
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves location relevant columns for locations.

        Returns:
        - A dictionary containing the count of locations and their details.
        """
        return self.run_endpoint(get_locations_for_map_wrapper)
