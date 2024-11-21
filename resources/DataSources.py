from flask import Response

from config import limiter
from middleware.access_logic import (
    AccessInfo,
    WRITE_ONLY_AUTH_INFO,
    GET_AUTH_INFO,
    STANDARD_JWT_AUTH_INFO,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryCreateUpdateRequestDTO,
    EntryDataRequestSchema,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    endpoint_info,
    endpoint_info_2,
)
from middleware.primary_resource_logic.data_sources_logic import (
    get_data_sources_wrapper,
    data_source_by_id_wrapper,
    add_new_data_source_wrapper,
    update_data_source_wrapper,
    DataSourcesGetManyRequestDTO,
    delete_data_source_wrapper,
    create_data_source_related_agency,
    delete_data_source_related_agency,
    get_data_source_related_agencies,
    get_data_sources_for_map_wrapper,
)

from middleware.schema_and_dto_logic.primary_resource_schemas.data_sources_advanced_schemas import (
    DataSourcesGetManyRequestSchema,
)
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import (
    create_response_dictionary,
    ResponseInfo,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource

from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters

namespace_data_source = create_namespace(AppNamespaces.DATA_SOURCES)

# This endpoint no longer works because of the other data source endpoint
# It is interpreted as another data source id
# But we have not yet decided whether to modify or remove it entirely


@namespace_data_source.route("/<resource_id>")
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_GET_BY_ID,
        response_info=ResponseInfo(
            success_message="Returns information on the specific data source.",
        ),
        description="Get details of a specific data source by its ID.",
    )
    @limiter.limit("50/minute;250/hour")
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

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_PUT,
        response_info=ResponseInfo(
            success_message="Data source successfully updated.",
        ),
        description="Update details of a specific data source by its ID.",
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
                dto_class=EntryCreateUpdateRequestDTO,
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

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns all requested data sources.",
        ),
        description="Retrieves all data sources.",
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

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Data source successfully added.",
        ),
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
            schema_populate_parameters=SchemaConfigs.DATA_SOURCES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )


# region Related Agencies


@namespace_data_source.route("/<resource_id>/related-agencies")
class DataSourcesRelatedAgencies(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_GET,
        response_info=ResponseInfo(
            success_message="Related agencies successfully retrieved.",
        ),
        description="Get related agencies to a data source",
    )
    def get(self, resource_id: str, access_info: AccessInfo) -> Response:
        """
        Get related agencies to a data source.
        """
        return self.run_endpoint(
            wrapper_function=get_data_source_related_agencies,
            schema_populate_parameters=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_GET.value.get_schema_populate_parameters(),
        )


@namespace_data_source.route("/<resource_id>/related-agencies/<agency_id>")
class DataSourcesRelatedAgenciesById(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_POST,
        response_info=ResponseInfo(
            success_message="Data source successfully associated with data request.",
        ),
        description="Mark a data source as related to a data request",
    )
    def post(
        self, resource_id: str, agency_id: str, access_info: AccessInfo
    ) -> Response:
        """
        Mark a data source as related to a data request
        """
        return self.run_endpoint(
            wrapper_function=create_data_source_related_agency,
            schema_populate_parameters=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info_2(
        namespace=namespace_data_source,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_DELETE,
        response_info=ResponseInfo(
            success_message="Data source successfully removed from data request.",
        ),
        description="Remove an association of a data source with a data request",
    )
    def delete(
        self, resource_id: str, agency_id: str, access_info: AccessInfo
    ) -> Response:
        """
        Remove an association of a data source with a data request
        """
        return self.run_endpoint(
            wrapper_function=delete_data_source_related_agency,
            schema_populate_parameters=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_DELETE.value.get_schema_populate_parameters(),
            access_info=access_info,
        )


# endregion
