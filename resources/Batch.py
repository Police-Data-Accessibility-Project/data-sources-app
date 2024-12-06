from middleware.access_logic import WRITE_ONLY_AUTH_INFO, STANDARD_JWT_AUTH_INFO, AccessInfoPrimary
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.batch_logic import batch_post_agency
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo
from utilities.namespace import create_namespace, AppNamespaces

namespace_batch = create_namespace(AppNamespaces.BATCH)


def add_csv_description(initial_description: str) -> str:
    return (
        f"{initial_description}\n\n"
        f"Note: Only file upload should be provided.\n"
        f"The json arguments simply denote the columns of the csv"
    )


@namespace_batch.route("/agencies")
class AgenciesBatch(PsycopgResource):

    @endpoint_info(
        namespace=namespace_batch,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.BATCH_AGENCIES_POST,
        description=add_csv_description(
            initial_description="Adds multiple agencies from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary):
        self.run_endpoint(
            wrapper_function=batch_post_agency,
            access_info=access_info,
            schema_populate_parameters=SchemaConfigs.BATCH_AGENCIES_POST.value.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_batch,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.BATCH_AGENCIES_PUT,
        description=add_csv_description(
            initial_description="Updates multiple agencies from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources updated successfully."
        ),
    )
    def put(self, access_info: AccessInfoPrimary):
        pass


@namespace_batch.route("/data-sources")
class DataSourcesBatch(PsycopgResource):

    @endpoint_info(
        namespace=namespace_batch,
        auth_info=STANDARD_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.BATCH_DATA_SOURCES_POST,
        description=add_csv_description(
            initial_description="Adds multiple data sources from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources created successfully."
        ),
    )
    def post(self, access_info: AccessInfoPrimary):
        pass

    @endpoint_info(
        namespace=namespace_batch,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.BATCH_DATA_SOURCES_PUT,
        description=add_csv_description(
            initial_description="Updates multiple data sources from a CSV file."
        ),
        response_info=ResponseInfo(
            success_message="At least some resources updated successfully."
        ),
    )
    def put(self, access_info: AccessInfoPrimary):
        pass
