from flask import Response

from config import limiter
from endpoints._helpers.response_info import ResponseInfo
from endpoints.instantiations.data_sources_.get.by_id.agencies.middleware import (
    get_data_source_related_agencies,
)
from endpoints.instantiations.data_sources_.get.by_id.wrapper import (
    data_source_by_id_wrapper,
)
from endpoints.instantiations.data_sources_.post.request_.wrapper import (
    post_data_source_wrapper,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.data_sources.by_id.agencies.get import (
    DataSourcesRelatedAgenciesGet,
)
from endpoints.schema_config.instantiations.data_sources.get_many import (
    DataSourcesGetManyEndpointSchemaConfig,
)
from middleware.decorators.endpoint_info import (
    endpoint_info,
)
from middleware.primary_resource_logic.data_sources import (
    get_data_sources_wrapper,
)
from middleware.schema_and_dto.dtos.common.base import GetByIDBaseDTO
from middleware.schema_and_dto.non_dto_dataclasses import SchemaPopulateParameters
from middleware.schema_and_dto.schemas.common.base import GetByIDBaseSchema
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import (
    API_OR_JWT_AUTH_INFO,
    STANDARD_JWT_AUTH_INFO,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_source = create_namespace(AppNamespaces.DATA_SOURCES)


@namespace_data_source.route("/<resource_id>")
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_GET_BY_ID,
        response_info=ResponseInfo(
            success_message="Returns information on the specific data source.",
        ),
        description="Get details of a specific data source by its ID.",
    )
    @limiter.limit("50/minute;250/hour")
    def get(self, access_info: AccessInfoPrimary, resource_id: str) -> Response:
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


@namespace_data_source.route("")
class DataSources(PsycopgResource):
    """
    A resource for managing collections of data sources.
    Provides methods for retrieving all data sources and adding new ones.
    """

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns all requested data sources.",
        ),
        description="Retrieves all data sources.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves all data sources. The data sources endpoint returns all approved rows in the corresponding Data
        Sources database table.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        return self.run_endpoint(
            wrapper_function=get_data_sources_wrapper,
            schema_populate_parameters=DataSourcesGetManyEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_POST,
        response_info=ResponseInfo(
            success_message="Returns the id of the newly created data source.",
        ),
        description="Creates a new data source.",
    )
    def post(self, access_info: AccessInfoPrimary):
        """
        Creates a new data source.
        """
        return self.run_endpoint(
            wrapper_function=post_data_source_wrapper,
            schema_populate_parameters=SchemaConfigs.DATA_SOURCES_POST.value.get_schema_populate_parameters(),
        )


# region Related Agencies


@namespace_data_source.route("/<resource_id>/related-agencies")
class DataSourcesRelatedAgencies(PsycopgResource):
    @endpoint_info(
        namespace=namespace_data_source,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.DATA_SOURCES_RELATED_AGENCIES_GET,
        response_info=ResponseInfo(
            success_message="Related agencies successfully retrieved.",
        ),
        description="Get related agencies to a data source",
    )
    @limiter.limit("50/minute;250/hour")
    def get(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        """
        Get related agencies to a data source.
        """
        return self.run_endpoint(
            wrapper_function=get_data_source_related_agencies,
            schema_populate_parameters=DataSourcesRelatedAgenciesGet.get_schema_populate_parameters(),
        )


# endregion
