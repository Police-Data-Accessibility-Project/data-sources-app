from flask import Response

from middleware.access_logic import (
    AccessInfoPrimary,
)
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO, API_OR_JWT_AUTH_INFO
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.locations_logic import (
    get_location_by_id_wrapper,
    get_locations_related_data_requests_wrapper,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_locations = create_namespace(AppNamespaces.LOCATIONS)


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
            schema_populate_parameters=SchemaConfigs.LOCATIONS_RELATED_DATA_REQUESTS_GET.value.get_schema_populate_parameters(),
        )
