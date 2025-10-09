from flask import Response

from config import limiter
from endpoints._helpers.docs import column_permissions_description
from endpoints._helpers.response_info import ResponseInfo
from endpoints.psycopg_resource import PsycopgResource
from endpoints.schema_config.enums import SchemaConfigs
from endpoints.schema_config.instantiations.agencies.by_id.get import (
    AgenciesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.agencies.get_many import (
    AgenciesGetManyEndpointSchemaConfig,
)
from middleware.column_permission.format import create_column_permissions_string_table
from middleware.decorators.endpoint_info import (
    endpoint_info,
)
from middleware.enums import Relations
from middleware.primary_resource_logic.agencies import (
    get_agencies,
    get_agency_by_id,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import (
    API_OR_JWT_AUTH_INFO,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_agencies = create_namespace(
    AppNamespaces.AGENCIES,
)


@namespace_agencies.route("")
class AgenciesByPage(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of approved agencies."
        ),
        description="Get a paginated list of approved agencies",
    )
    def get(self, access_info: AccessInfoPrimary) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        return self.run_endpoint(
            wrapper_function=get_agencies,
            schema_populate_parameters=AgenciesGetManyEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )



@namespace_agencies.route("/<resource_id>")
class AgenciesById(PsycopgResource):
    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_BY_ID_GET,
        response_info=ResponseInfo(
            success_message="Returns information on the specific agency."
        ),
        description=column_permissions_description(
            head_description="Get an agency by id",
            sub_description="Columns returned are determined by the user's access level.",
            column_permissions_str_table=create_column_permissions_string_table(
                relation=Relations.AGENCIES.value
            ),
        ),
    )
    @limiter.limit("50/minute;250/hour")
    def get(self, resource_id: str, access_info: AccessInfoPrimary) -> Response:
        return self.run_endpoint(
            wrapper_function=get_agency_by_id,
            schema_populate_parameters=AgenciesByIDGetEndpointSchemaConfig.get_schema_populate_parameters(),
            access_info=access_info,
        )

