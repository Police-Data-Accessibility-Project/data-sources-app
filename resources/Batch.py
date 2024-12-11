from flask import Response

from middleware.access_logic import (
    WRITE_ONLY_AUTH_INFO,
    STANDARD_JWT_AUTH_INFO,
    AccessInfoPrimary,
)
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.bulk_logic import (
    bulk_post_agencies,
    bulk_post_data_sources,
    bulk_put_agencies,
    bulk_put_data_sources,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
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
            success_message="At least some resources created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=bulk_post_agencies,
            schema_populate_parameters=SchemaConfigs.BULK_AGENCIES_POST.value.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_bulk,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.BULK_AGENCIES_PUT,
        description=add_csv_description(
            initial_description="Updates multiple agencies from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources updated successfully."
        ),
    )
    def put(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=bulk_put_agencies,
            schema_populate_parameters=SchemaConfigs.BULK_AGENCIES_PUT.value.get_schema_populate_parameters(),
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
            success_message="At least some resources created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary):
        return self.run_endpoint(
            wrapper_function=bulk_post_data_sources,
            schema_populate_parameters=SchemaConfigs.BULK_DATA_SOURCES_POST.value.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_bulk,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.BULK_DATA_SOURCES_PUT,
        description=add_csv_description(
            initial_description="Updates multiple data sources from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources updated successfully."
        ),
    )
    def put(self, access_info: AccessInfoPrimary):

        return self.run_endpoint(
            wrapper_function=bulk_put_data_sources,
            schema_populate_parameters=SchemaConfigs.BULK_DATA_SOURCES_PUT.value.get_schema_populate_parameters(),
        )
