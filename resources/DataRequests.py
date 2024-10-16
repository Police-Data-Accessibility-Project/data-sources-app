from flask import Response

from middleware.access_logic import (
    AccessInfo,
    GET_AUTH_INFO,
    OWNER_WRITE_ONLY_AUTH_INFO,
)
from middleware.primary_resource_logic.data_requests import (
    create_data_request_wrapper,
    get_data_requests_wrapper,
    delete_data_request_wrapper,
    update_data_request_wrapper,
    get_data_request_by_id_wrapper,
    delete_data_request_related_source,
    get_data_request_related_sources,
    create_data_request_related_source,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryCreateUpdateRequestDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    endpoint_info,
    endpoint_info_2,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_schemas import (
    DataRequestsSchema,
)
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import (
    create_response_dictionary,
    ResponseInfo,
)
from resources.endpoint_schema_config import SchemaConfigs
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)


@namespace_data_requests.route("/<resource_id>")
class DataRequestsById(PsycopgResource):

    # TODO: More thoroughly update to endpoint_info_2
    @endpoint_info_2(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_BY_ID_GET,
        response_info=ResponseInfo(
            success_message="Returns information on the specific data request.",
        ),
        description="Get data request by id",
    )
    def get(self, access_info: AccessInfo, resource_id: str) -> Response:
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

    # TODO: Modify to endpoint_info_2
    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        input_schema=DataRequestsSchema(
            exclude=[
                "id",
                "date_created",
                "date_status_last_changed",
                "creator_user_id",
            ]
        ),
        input_model_name="DataRequestPutSchema",
        description="Update data request",
        responses=create_response_dictionary(
            success_message="Data request successfully updated.",
        ),
    )
    def put(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Update data request. Non-admins can only update their own data requests.
        """
        return self.run_endpoint(
            update_data_request_wrapper,
            dto_populate_parameters=EntryCreateUpdateRequestDTO.get_dto_populate_parameters(),
            data_request_id=int(resource_id),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        description="Delete a data request by its ID",
        responses=create_response_dictionary(
            success_message="Data request successfully deleted."
        ),
    )
    def delete(self, resource_id: str, access_info: AccessInfo) -> Response:
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

    @endpoint_info_2(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of data requests.",
        ),
        description="Get data requests with optional filters",
    )
    def get(self, access_info: AccessInfo) -> Response:
        """
        Get data requests
        """
        return self.run_endpoint(
            wrapper_function=get_data_requests_wrapper,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_GET_MANY.value.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info_2(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_POST,
        response_info=ResponseInfo(
            success_message="Data request successfully created.",
        ),
        description="Create new data request",
    )
    def post(self, access_info: AccessInfo) -> Response:
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

    @endpoint_info_2(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_GET,
        response_info=ResponseInfo(
            success_message="Related sources successfully retrieved.",
        ),
        description="Get sources related to a data request",
    )
    def get(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Get sources marked as related to a data request.
        """
        return self.run_endpoint(
            wrapper_function=get_data_request_related_sources,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_GET.value.get_schema_populate_parameters(),
        )


@namespace_data_requests.route("/<resource_id>/related-sources/<data_source_id>")
class DataRequestsRelatedSourcesById(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Data source successfully associated with data request.",
        ),
        description="Mark a data source as related to a data request",
    )
    def post(
        self, resource_id: str, data_source_id: str, access_info: AccessInfo
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
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        description="""Delete an association of a data source with a data request""",
        responses=create_response_dictionary(
            success_message="Successfully removed data source association from data request.",
        ),
    )
    def delete(
        self, resource_id: str, data_source_id: str, access_info: AccessInfo
    ) -> Response:
        """
        Remove an association of a data source with a data request
        """
        return self.run_endpoint(
            wrapper_function=delete_data_request_related_source,
            schema_populate_parameters=SchemaConfigs.DATA_REQUESTS_RELATED_SOURCES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
