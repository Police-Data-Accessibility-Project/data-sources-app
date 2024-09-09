from flask import Response

from middleware.access_logic import AccessInfo
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    EntryDataRequestSchema,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    api_key_required,
    authentication_required,
)
from middleware.primary_resource_logic.data_source_queries import (
    get_data_sources_wrapper,
    data_source_by_id_wrapper,
    get_data_sources_for_map_wrapper,
    add_new_data_source_wrapper,
    update_data_source_wrapper,
    DataSourcesGetRequestSchemaMany,
    DataSourcesGetRequestDTOMany,
    delete_data_source_wrapper,
)
from middleware.enums import PermissionsEnum, AccessTypeEnum
from middleware.schema_and_dto_logic.model_helpers_with_schemas import (
    CRUDModels,
)
from resources.resource_helpers import (
    add_api_key_header_arg,
    add_jwt_header_arg,
    create_response_dictionary,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from middleware.schema_and_dto_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_data_source = create_namespace(AppNamespaces.DATA_SOURCES)

models = CRUDModels(namespace_data_source)

data_sources_get_request_parser = get_restx_param_documentation(
    namespace=namespace_data_source,
    schema_class=DataSourcesGetRequestSchemaMany,
    model_name="DataSourcesGetRequest",
).parser

authorization_api_parser = namespace_data_source.parser()
add_api_key_header_arg(authorization_api_parser)

authorization_jwt_parser = namespace_data_source.parser()
add_jwt_header_arg(authorization_jwt_parser)


@namespace_data_source.route("/<resource_id>")
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @handle_exceptions
    @authentication_required([AccessTypeEnum.API_KEY, AccessTypeEnum.JWT])
    @namespace_data_source.doc(
        description="Get details of a specific data source by its ID.",
        responses=create_response_dictionary(
            success_message="Returns information on the specific data source.",
            success_model=models.entry_data_response_model,
        ),
    )
    @namespace_data_source.expect(authorization_api_parser)
    def get(self, access_info: AccessInfo, resource_id: str) -> Response:
        """
        Retrieves details of a specific data source by its ID.

        Parameters:
        - data_source_id (str): The unique identifier of the data source.

        Returns:
        - Tuple containing the response message with data source details if found, and the HTTP status code.
        """
        return self.run_endpoint(
            data_source_by_id_wrapper,
            access_info=access_info,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=GetByIDBaseSchema, dto_class=GetByIDBaseDTO
            ),
        )

    @handle_exceptions
    @authentication_required(
        [AccessTypeEnum.JWT], restrict_to_permissions=[PermissionsEnum.DB_WRITE]
    )
    @namespace_data_source.expect(
        authorization_jwt_parser, models.entry_data_request_model
    )
    @namespace_data_source.doc(
        description="Update details of a specific data source by its ID.",
        responses=create_response_dictionary(
            success_message="Data source successfully updated.",
        ),
    )
    def put(self, access_info: AccessInfo, resource_id: str) -> Response:
        """
        Updates a data source by its ID based on the provided JSON payload.

        Parameters:
        - data_source_id (str): The unique identifier of the data source to update.

        Returns:
        - A dictionary containing a message about the update operation.
        """
        return self.run_endpoint(
            wrapper_function=update_data_source_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                dto_class=EntryDataRequestDTO,
                schema_class=EntryDataRequestSchema,
            ),
            data_source_id=resource_id,
            access_info=access_info,
        )

    @handle_exceptions
    @authentication_required(
        [AccessTypeEnum.JWT], restrict_to_permissions=[PermissionsEnum.DB_WRITE]
    )
    @namespace_data_source.doc(
        description="Delete a data source by its ID.",
        responses=create_response_dictionary(
            success_message="Data source successfully deleted."
        ),
    )
    @namespace_data_source.expect(authorization_jwt_parser)
    def delete(self, access_info: AccessInfo, resource_id: str) -> Response:
        """
        Deletes a data source by its ID.

        Parameters:
        - data_source_id (str): The unique identifier of the data source to delete.

        Returns:
        - A dictionary containing a message about the deletion operation.
        """
        return self.run_endpoint(
            wrapper_function=delete_data_source_wrapper,
            data_source_id=resource_id,
            access_info=access_info,
        )


@namespace_data_source.route("")
class DataSources(PsycopgResource):
    """
    A resource for managing collections of data sources.
    Provides methods for retrieving all data sources and adding new ones.
    """

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
    )
    @namespace_data_source.doc(
        description="Retrieves all data sources.",
        responses=create_response_dictionary(
            success_message="Returns all requested data sources.",
            success_model=models.get_many_response_model,
        ),
    )
    @namespace_data_source.expect(
        data_sources_get_request_parser, authorization_api_parser
    )
    def get(self, access_info: AccessInfo) -> Response:
        """
        Retrieves all data sources. The data sources endpoint returns all approved rows in the corresponding Data
        Sources database table.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        return self.run_endpoint(
            wrapper_function=get_data_sources_wrapper,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=DataSourcesGetRequestSchemaMany,
                dto_class=DataSourcesGetRequestDTOMany,
            ),
            access_info=access_info,
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
        restrict_to_permissions=[PermissionsEnum.DB_WRITE],
    )
    @namespace_data_source.expect(
        authorization_jwt_parser, models.entry_data_request_model
    )
    @namespace_data_source.doc(
        description="Adds a new data source.",
        responses=create_response_dictionary(
            success_message="Data source successfully added.",
            success_model=models.id_and_message_model,
        ),
    )
    def post(self, access_info: AccessInfo) -> Response:
        """
        Adds a new data source based on the provided JSON payload.

        Returns:
        - A dictionary containing a message about the addition operation.
        """
        return self.run_endpoint(
            wrapper_function=add_new_data_source_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            access_info=access_info,
        )

    # This endpoint no longer works because of the other data source endpoint
    # It is interpreted as another data source id
    # But we have not yet decided whether to modify or remove it entirely
# @namespace_data_source.route("/data-sources-map")
# class DataSourcesMap(PsycopgResource):
#     """
#     A resource for managing collections of data sources for mapping.
#     Provides a method for retrieving all data sources.
#     """
#
#     @handle_exceptions
#     @authentication_required(
#         allowed_access_methods=[AccessTypeEnum.API_KEY],
#     )
#     @namespace_data_source.response(200, "Success", models.get_many_response_model)
#     @namespace_data_source.response(500, "Internal server error")
#     @namespace_data_source.response(400, "Bad request; missing or bad API key")
#     @namespace_data_source.response(403, "Forbidden; invalid API key")
#     @namespace_data_source.doc(
#         description="Retrieves location-relevant columns for data sources.",
#     )
#     @namespace_data_source.expect(authorization_api_parser)
#     def get(self) -> Response:
#         """
#         Retrieves location relevant columns for data sources.
#
#         Returns:
#         - A dictionary containing the count of data sources and their details.
#         """
#         return self.run_endpoint(get_data_sources_for_map_wrapper)
