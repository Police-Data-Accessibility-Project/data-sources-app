from flask import Response

from middleware.access_logic import (
    AccessInfo,
    WRITE_ONLY_AUTH_INFO,
    GET_AUTH_INFO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    EntryDataRequestSchema,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    endpoint_info,
)
from middleware.primary_resource_logic.data_sources_logic import (
    get_data_sources_wrapper,
    data_source_by_id_wrapper,
    add_new_data_source_wrapper,
    update_data_source_wrapper,
    DataSourcesGetManyRequestDTO,
    delete_data_source_wrapper,
)
from middleware.schema_and_dto_logic.dynamic_logic.dynamic_schema_documentation_construction import (
    get_restx_param_documentation,
)
from middleware.schema_and_dto_logic.dynamic_logic.model_helpers_with_schemas import (
    CRUDModels,
)
from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_schemas import DataSourcesGetByIDSchema, \
    DataSourcesGetManySchema, DataSourcesGetManyRequestSchema, DataSourcesPostSchema, DataSourcesPutSchema
from resources.resource_helpers import (
    create_response_dictionary,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource

from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_data_source = create_namespace(AppNamespaces.DATA_SOURCES)
models = CRUDModels(namespace_data_source)

get_by_id_model = get_restx_param_documentation(
    namespace=namespace_data_source,
    schema=DataSourcesGetByIDSchema,
    model_name="DataSourcesGetByIDSchema",
).model

get_many_model = get_restx_param_documentation(
    namespace=namespace_data_source,
    schema=DataSourcesGetManySchema,
    model_name="DataSourcesGetManySchema",
).model


@namespace_data_source.route("/<resource_id>")
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=GET_AUTH_INFO,
        responses=create_response_dictionary(
            success_message="Returns information on the specific data source.",
            success_model=get_by_id_model,
        ),
    )
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
                schema=GetByIDBaseSchema(), dto_class=GetByIDBaseDTO
            ),
        )

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        input_schema=DataSourcesPutSchema(),
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
                schema=EntryDataRequestSchema(),
            ),
            data_source_id=resource_id,
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        responses=create_response_dictionary(
            success_message="Data source successfully deleted.",
        ),
    )
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

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=GET_AUTH_INFO,
        input_schema=DataSourcesGetManyRequestSchema(),
        description="Retrieves all data sources.",
        responses=create_response_dictionary(
            success_message="Returns all requested data sources.",
            success_model=get_many_model,
        ),
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
                schema=DataSourcesGetManyRequestSchema(),
                dto_class=DataSourcesGetManyRequestDTO,
            ),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        responses=create_response_dictionary(
            success_message="Data source successfully added.",
            success_model=models.id_and_message_model,
        ),
        input_schema=DataSourcesPostSchema(),
        description="Adds a new data source.",
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
