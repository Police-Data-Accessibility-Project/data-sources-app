from flask import Response

from config import limiter
from middleware.access_logic import (
    AccessInfoPrimary,
)
from middleware.authentication_info import STANDARD_JWT_AUTH_INFO, API_OR_JWT_AUTH_INFO
from middleware.primary_resource_logic.data_requests import (
    create_data_request_wrapper,
    get_data_requests_wrapper,
    delete_data_request_wrapper,
    update_data_request_wrapper,
    get_data_request_by_id_wrapper,
    delete_data_request_related_source,
    get_data_request_related_sources,
    create_data_request_related_source,
    get_data_request_related_locations,
    create_data_request_related_location,
    delete_data_request_related_location,
    withdraw_data_request_wrapper,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    endpoint_info,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import (
    ResponseInfo,
)
from resources.endpoint_schema_config import SchemaConfigs
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)


@namespace_data_requests.route("/<resource_id>")
class DataRequestsById(PsycopgResource):

    # TODO: More thoroughly update to endpoint_info_2
    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_BY_ID_GET,
        response_info=ResponseInfo(
            success_message="Returns information on the specific data request.",
        ),
        description="Get data request by id",
    )
    @limiter.limit("50/minute;250/hour")
    def get(self, access_info: AccessInfoPrimary, resource_id: str) -> Response:
        """
        Get data request by id
        """
        return self.run_endpoint(
            get_data_request_by_id_wrapper,
            access_info=access_info,
            schema_populate_parameters=SchemaPopulateParameters(
                schema=GetByIDBaseSchema(), dto_class=GetByIDBaseDTO
            ),
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        description="Update data request.",
        response_info=ResponseInfo(
            success_message="Data request successfully updated.",
        ),
        schema_config=SchemaConfigs.DATA_REQUESTS_BY_ID_PUT,
    )
    def put(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Update data request. Non-admins can only update their own data requests.
        """
        return self.run_endpoint(
            update_data_request_wrapper,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_BY_ID_PUT.value.get_schema_populate_parameters(),
            data_request_id=int(resource_id),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        description="Delete a data request by its ID",
        response_info=ResponseInfo(
            success_message="Data request successfully deleted.",
        ),
        schema_config=SchemaConfigs.DATA_REQUESTS_BY_ID_DELETE,
    )
    def delete(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Delete data request
        """
        return self.run_endpoint(
            delete_data_request_wrapper,
            data_request_id=int(resource_id),
            access_info=access_info,
        )


@namespace_data_requests.route("")
class DataRequests(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of data requests.",
        ),
        description="Get data requests with optional filters",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Get data requests
        """
        return self.run_endpoint(
            wrapper_function=get_data_requests_wrapper,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_GET_MANY.value.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_POST,
        response_info=ResponseInfo(
            success_message="Data request successfully created.",
        ),
        description="Create new data request",
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Create a new data request.
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_wrapper,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )


@namespace_data_requests.route("/<resource_id>/related-sources")
class DataRequestsRelatedSources(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_GET,
        response_info=ResponseInfo(
            success_message="Related sources successfully retrieved.",
        ),
        description="Get sources related to a data request",
    )
    def get(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Get sources marked as related to a data request.
        """
        return self.run_endpoint(
            wrapper_function=get_data_request_related_sources,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_GET.value.get_schema_populate_parameters(),
        )


@namespace_data_requests.route("/<resource_id>/related-sources/<data_source_id>")
class DataRequestsRelatedSourcesById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Data source successfully associated with data request.",
        ),
        description="Mark a data source as related to a data request",
    )
    def post(
        self, resource_id: str, data_source_id: str, access_info: AccessInfoPrimary
    ) -> Response:
        """
        Mark a data source as related to a data request
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_related_source,
            access_info=access_info,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST.value.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Successfully removed data source association from data request.",
        ),
    )
    def delete(
        self, resource_id: str, data_source_id: str, access_info: AccessInfoPrimary
    ) -> Response:
        """
        Remove an association of a data source with a data request
        """
        return self.run_endpoint(
            wrapper_function=delete_data_request_related_source,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )


@namespace_data_requests.route("/<resource_id>/withdraw")
class DataRequestsWithdraw(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_BY_ID_WITHDRAW,
        response_info=ResponseInfo(
            success_message="Data request successfully withdrawn.",
        ),
    )
    def post(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Withdraw a data request
        """
        return self.run_endpoint(
            wrapper_function=withdraw_data_request_wrapper,
            data_request_id=int(resource_id),
            access_info=access_info,
        )


@namespace_data_requests.route("/<resource_id>/related-locations")
class DataRequestsRelatedLocations(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_GET,
        response_info=ResponseInfo(
            success_message="Related locations successfully retrieved.",
        ),
        description="Get locations related to a data request",
    )
    def get(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Get locations marked as related to a data request.
        """
        return self.run_endpoint(
            wrapper_function=get_data_request_related_locations,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_GET.value.get_schema_populate_parameters(),
        )


@namespace_data_requests.route("/<resource_id>/related-locations/<location_id>")
class DataRequestsRelatedLocationsById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_POST,
        response_info=ResponseInfo(
            success_message="Location successfully associated with data request.",
        ),
        description="Mark a location as related to a data request",
    )
    def post(self, resource_id: str, location_id: str, access_info: AccessInfoPrimary):
        """
        Mark a location as related to a data request
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_related_location,
            access_info=access_info,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_POST.value.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_POST,
        description="""Delete an association of a location with a data request""",
        response_info=ResponseInfo(
            success_message="Successfully removed location association from data request.",
        ),
    )
    def delete(
        self, resource_id: str, location_id: str, access_info: AccessInfoPrimary
    ):
        """
        Remove an association of a location with a data request
        """
        return self.run_endpoint(
            wrapper_function=delete_data_request_related_location,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_LOCATIONS_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
