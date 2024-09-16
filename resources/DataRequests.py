from flask import Response

from middleware.access_logic import (
    AccessInfo,
    GET_AUTH_INFO,
    OWNER_WRITE_ONLY_AUTH_INFO,
)
from middleware.column_permission_logic import create_column_permissions_string_table
from middleware.primary_resource_logic.data_requests import (
    create_data_request_wrapper,
    get_data_requests_wrapper,
    delete_data_request_wrapper,
    update_data_request_wrapper,
    get_data_request_by_id_wrapper,
    delete_data_request_related_source,
    get_data_request_related_sources,
    create_data_request_related_source,
    RelatedSourceByIDDTO,
    RelatedSourceByIDSchema,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    endpoint_info,
)
from middleware.enums import  Relations
from middleware.schema_and_dto_logic.model_helpers_with_schemas import (
    create_entry_data_request_model,
    create_id_and_message_model,
    create_get_many_response_model,
    create_entry_data_response_model,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import PsycopgResource
from resources.resource_helpers import (
    create_response_dictionary,
    column_permissions_description,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)

entry_data_requests_model = create_entry_data_request_model(namespace_data_requests)
entry_data_response_model = create_entry_data_response_model(namespace_data_requests)
data_requests_outer_model = create_get_many_response_model(namespace_data_requests)
id_and_message_model = create_id_and_message_model(namespace_data_requests)

data_requests_column_permissions = create_column_permissions_string_table(
    relation=Relations.DATA_REQUESTS.value
)


@namespace_data_requests.route("/<resource_id>")
class DataRequestsById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        description=column_permissions_description(
            head_description="Get data request by id",
            sub_description="Columns returned are determinant upon the user's "
            "access level and/or relation to the data request",
            column_permissions_str_table=data_requests_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Returns information on the specific data request.",
            success_model=entry_data_response_model,
        ),
    )
    def get(self, access_info: AccessInfo, resource_id: str) -> Response:
        """
        Get data request by id
        :return:
        """
        return self.run_endpoint(
            get_data_request_by_id_wrapper,
            access_info=access_info,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=GetByIDBaseSchema, dto_class=GetByIDBaseDTO
            ),
        )

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        description=column_permissions_description(
            head_description="Update data request",
            sub_description="Columns returned are determinant upon the user's "
            "access level and/or relation to the data request",
            column_permissions_str_table=data_requests_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Data request successfully updated.",
        ),
    )
    def put(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Update data request
        :return:
        """
        return self.run_endpoint(
            update_data_request_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
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

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        description=column_permissions_description(
            head_description="Get data requests with optional filters",
            sub_description="For non-admins, data requests the user created will be returned first "
            "and will include additional columns to reflect ownership",
            column_permissions_str_table=data_requests_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Returns a paginated list of data requests.",
            success_model=data_requests_outer_model,
        ),
    )
    def get(self, access_info: AccessInfo) -> Response:
        return self.run_endpoint(get_data_requests_wrapper, access_info=access_info)

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        description=column_permissions_description(
            head_description="Create new data request",
            sub_description="Columns permitted to be included by the user is determined by their level of access",
            column_permissions_str_table=data_requests_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Data request successfully created.",
            success_model=id_and_message_model,
        ),
    )
    def post(self, access_info: AccessInfo) -> Response:
        """
        Creates a new data request
        :return:
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            access_info=access_info,
        )


@namespace_data_requests.route("/<resource_id>/related-sources")
class DataRequestsRelatedSources(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=GET_AUTH_INFO,
        description="""Get sources related to a data request""",
        responses=create_response_dictionary(
            success_message="Related sources successfully retrieved.",
            success_model=data_requests_outer_model,
        ),
    )
    def get(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=get_data_request_related_sources,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=GetByIDBaseSchema, dto_class=GetByIDBaseDTO
            ),
        )


@namespace_data_requests.route("/<resource_id>/related-sources/<data_source_id>")
class DataRequestsRelatedSourcesById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_data_requests,
        auth_info=OWNER_WRITE_ONLY_AUTH_INFO,
        description="""Add an association of a data source with a data request""",
        responses=create_response_dictionary(
            success_message="Data source successfully associated with data request.",
        ),
    )
    def post(
        self, resource_id: str, data_source_id: str, access_info: AccessInfo
    ) -> Response:
        return self.run_endpoint(
            wrapper_function=create_data_request_related_source,
            access_info=access_info,
            schema_populate_parameters=SchemaPopulateParameters(
                dto_class=RelatedSourceByIDDTO,
                schema_class=RelatedSourceByIDSchema,
            ),
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
        return self.run_endpoint(
            wrapper_function=delete_data_request_related_source,
            schema_populate_parameters=SchemaPopulateParameters(
                dto_class=RelatedSourceByIDDTO,
                schema_class=RelatedSourceByIDSchema,
            ),
            access_info=access_info,
        )
