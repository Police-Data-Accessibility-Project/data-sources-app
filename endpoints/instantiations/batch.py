from flask import Response

from endpoints.schema_config.instantiations.bulk.agencies import (
    BulkAgenciesPostEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.bulk.data_sources import (
    BulkDataSourcesPostEndpointSchemaConfig,
)
from middleware.access_logic import (
    AccessInfoPrimary,
)
from middleware.security.authentication_info import STANDARD_JWT_AUTH_INFO
from middleware.decorators.decorators import endpoint_info
from middleware.primary_resource_logic.bulk import (
    bulk_post_agencies,
    bulk_post_data_sources,
)
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_bulk = create_namespace(AppNamespaces.BULK)


def add_csv_description(initial_description: str) -> str:
    return (
        f"{initial_description}\n\n"
        f"Note: Only file upload should be provided.\n"
        f"The json arguments simply denote the columns of the csv"
    )


@namespace_bulk.route("/agencies")
class AgenciesBulk(PsycopgResource):

    @endpoint_info(
        namespace=namespace_bulk,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.BULK_AGENCIES_POST,
        description=add_csv_description(
            initial_description="Adds multiple agencies from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some endpoints created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=bulk_post_agencies,
            schema_populate_parameters=BulkAgenciesPostEndpointSchemaConfig.get_schema_populate_parameters(),
        )


@namespace_bulk.route("/data-sources")
class DataSourcesBulk(PsycopgResource):

    @endpoint_info(
        namespace=namespace_bulk,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.BULK_DATA_SOURCES_POST,
        description=add_csv_description(
            initial_description="Adds multiple data sources from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some endpoints created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=bulk_post_data_sources,
            schema_populate_parameters=BulkDataSourcesPostEndpointSchemaConfig.get_schema_populate_parameters(),
        )
