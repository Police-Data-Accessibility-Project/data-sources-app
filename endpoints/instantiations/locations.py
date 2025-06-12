from flask import Response

from config import limiter
from endpoints.schema_config.instantiations.locations.by_id.put import (
    LocationsByIDPutEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.data_requests import (
    LocationsRelatedDataRequestsGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.locations.get_many import (
    LocationsGetManyEndpointSchemaConfig,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import (
    STANDARD_JWT_AUTH_INFO,
    API_OR_JWT_AUTH_INFO,
    WRITE_ONLY_AUTH_INFO,
)
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.locations import (
    get_location_by_id_wrapper,
    get_locations_related_data_requests_wrapper,
    update_location_by_id_wrapper,
    get_many_locations_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_locations = create_namespace(AppNamespaces.LOCATIONS)


@namespace_locations.route("")
class Locations(PsycopgResource):

    @endpoint_info(
        namespace=namespace_locations,
        description="Get all locations",
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.LOCATIONS_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of locations.",
        ),
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_many_locations_wrapper,
            schema_populate_parameters=LocationsGetManyEndpointSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_locations.route("/<int:location_id>")
class LocationsByID(PsycopgResource):

    @endpoint_info(
        namespace=namespace_locations,
        description="Get a location by ID",
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.LOCATIONS_BY_ID_GET,
        response_info=ResponseInfo(
            success_message="Returns a location by ID.",
        ),
    )
    def get(self, location_id: int, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_location_by_id_wrapper,
            location_id=int(location_id),
        )

    @endpoint_info(
        namespace=namespace_locations,
        description="Get a location by ID",
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.LOCATIONS_BY_ID_PUT,
        response_info=ResponseInfo(
            success_message="Successfully updates a location by ID.",
        ),
    )
    @limiter.limit("60/minute")
    def put(self, location_id: int, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=update_location_by_id_wrapper,
            schema_populate_parameters=LocationsByIDPutEndpointSchemaConfig.get_schema_populate_parameters(),
            location_id=int(location_id),
        )


@namespace_locations.route("/<resource_id>/data-requests")
class LocationsRelatedDataRequestsById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_locations,
        description="Get data requests associated with a location by ID",
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.LOCATIONS_RELATED_DATA_REQUESTS_GET,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of data requests associated with a location by ID.",
        ),
    )
    def get(self, resource_id: int, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_locations_related_data_requests_wrapper,
            access_info=access_info,
            schema_populate_parameters=LocationsRelatedDataRequestsGetEndpointSchemaConfig.get_schema_populate_parameters(),
        )
