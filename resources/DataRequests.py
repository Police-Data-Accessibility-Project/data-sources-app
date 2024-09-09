from flask import Response

from middleware.access_logic import AccessInfo
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
    authentication_required,
)
from middleware.enums import AccessTypeEnum, Relations
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import get_restx_param_documentation
from middleware.schema_and_dto_logic.model_helpers_with_schemas import (
    create_entry_data_request_model,
    create_id_and_message_model,
    create_get_many_response_model,
    create_entry_data_response_model,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
    create_response_dictionary,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)

entry_data_requests_model = create_entry_data_request_model(namespace_data_requests)
entry_data_response_model = create_entry_data_response_model(namespace_data_requests)
data_requests_outer_model = create_get_many_response_model(namespace_data_requests)
id_and_message_model = create_id_and_message_model(namespace_data_requests)

related_sources_by_id_doc_info = get_restx_param_documentation(
    namespace=namespace_data_requests,
    schema_class=RelatedSourceByIDSchema,
    model_name="RelatedSourceByID",
)

data_requests_column_permissions = create_column_permissions_string_table(
    relation=Relations.DATA_REQUESTS.value
)

authorization_parser = namespace_data_requests.parser()
add_jwt_or_api_key_header_arg(authorization_parser)


@namespace_data_requests.route("/<resource_id>")
class DataRequestsById(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description=f"""
        Get data request by id
        
Columns returned are determinant upon the user's access level and/or relation to the data request
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        """,
        responses=create_response_dictionary(
            success_message="Returns information on the specific data request.",
            success_model=entry_data_response_model,
        ),
        expect=[authorization_parser],
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

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description=f"""
        Updates data request
        
Columns allowed to be updated by the user is determinant upon the user's access level and/or relation to the data request:
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        
        """,
        responses=create_response_dictionary(
            success_message="Data request successfully updated.",
        ),
        expect=[authorization_parser, entry_data_requests_model],
    )
    def put(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Update data request
        :return:
        """
        return self.run_endpoint(
            update_data_request_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            data_request_id=resource_id,
            access_info=access_info,
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description="Delete a data request by its ID",
        responses=create_response_dictionary(
            success_message="Data request successfully deleted."
        ),
        expect=[authorization_parser],
    )
    def delete(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Delete data request
        """
        return self.run_endpoint(
            delete_data_request_wrapper,
            data_request_id=resource_id,
            access_info=access_info,
        )


@namespace_data_requests.route("")
class DataRequests(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description=f"""
        Gets data requests with optional filters
        For non-admins, data requests the user created will be returned first
        and will include additional columns to reflect ownership
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        """,
        responses=create_response_dictionary(
            success_message="Returns a paginated list of data requests.",
            success_model=data_requests_outer_model,
        ),
        expect=[authorization_parser],
    )
    def get(self, access_info: AccessInfo) -> Response:
        return self.run_endpoint(get_data_requests_wrapper, access_info=access_info)

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description=f"""
        Creates a new data request
        
Columns permitted to be included by the user is determined by their level of access
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        
        """,
        responses=create_response_dictionary(
            success_message="Data request successfully created.",
            success_model=id_and_message_model,
        ),
        expect=[entry_data_requests_model, authorization_parser],
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

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY],
    )
    @namespace_data_requests.doc(
        description="""Get sources related to a data request""",
        responses=create_response_dictionary(
            success_message="Related sources successfully retrieved.",
            success_model=data_requests_outer_model,
        ),
        expect=[authorization_parser],
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
    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
        description="""Add an association of a data source with a data request""",
        responses=create_response_dictionary(
            success_message="Data source successfully associated with data request.",
        ),
    )
    def post(self, resource_id: str, data_source_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=create_data_request_related_source,
            access_info=access_info,
            schema_populate_parameters=SchemaPopulateParameters(
                dto_class=RelatedSourceByIDDTO,
                schema_class=RelatedSourceByIDSchema,
            ),
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.doc(
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
