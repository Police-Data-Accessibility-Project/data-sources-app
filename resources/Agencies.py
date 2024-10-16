from flask import Response

from middleware.access_logic import AccessInfo, GET_AUTH_INFO, WRITE_ONLY_AUTH_INFO
from middleware.column_permission_logic import create_column_permissions_string_table
from middleware.decorators import (
    endpoint_info,
    endpoint_info_2,
)
from middleware.enums import Relations
from middleware.primary_resource_logic.agencies import (
    get_agencies,
    get_agency_by_id,
    create_agency,
    update_agency,
    delete_agency,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    GET_MANY_SCHEMA_POPULATE_PARAMETERS,
)
from resources.PsycopgResource import PsycopgResource
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import (
    create_response_dictionary,
    column_permissions_description,
    ResponseInfo,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_agencies = create_namespace(
    AppNamespaces.AGENCIES,
)
agencies_column_permissions = create_column_permissions_string_table(
    relation=Relations.AGENCIES.value
)


@namespace_agencies.route("")
class AgenciesByPage(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @endpoint_info_2(
        namespace=namespace_agencies,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_GET_MANY,
        response_info=ResponseInfo(
            success_message="Returns a paginated list of approved agencies."
        ),
        description="Get a paginated list of approved agencies",
    )
    def get(self, access_info: AccessInfo) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        return self.run_endpoint(
            wrapper_function=get_agencies,
            schema_populate_parameters=GET_MANY_SCHEMA_POPULATE_PARAMETERS,
            access_info=access_info,
        )

    @endpoint_info_2(
        namespace=namespace_agencies,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_POST,
        response_info=ResponseInfo(
            success_message="Returns the id of the newly created agency."
        ),
    )
    def post(self, access_info: AccessInfo):
        return self.run_endpoint(
            wrapper_function=create_agency,
            schema_populate_parameters=SchemaConfigs.AGENCIES_POST.value.get_schema_populate_parameters(),
            access_info=access_info,
        )


@namespace_agencies.route("/<resource_id>")
class AgenciesById(PsycopgResource):

    @endpoint_info_2(
        namespace=namespace_agencies,
        auth_info=GET_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_BY_ID_GET,
        response_info=ResponseInfo(
            success_message="Returns information on the specific agency."
        ),
        description=column_permissions_description(
            head_description="Get an agency by id",
            sub_description="Columns returned are determined by the user's access level.",
            column_permissions_str_table=agencies_column_permissions,
        ),
    )
    def get(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=get_agency_by_id,
            schema_populate_parameters=SchemaConfigs.AGENCIES_BY_ID_GET.value.get_schema_populate_parameters(),
            access_info=access_info,
        )

    @endpoint_info_2(
        namespace=namespace_agencies,
        auth_info=WRITE_ONLY_AUTH_INFO,
        schema_config=SchemaConfigs.AGENCIES_BY_ID_PUT,
        response_info=ResponseInfo(
            success_message="Returns information on the specific agency."
        ),
        description="Updates an agency",
    )
    def put(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            update_agency,
            access_info=access_info,
            agency_id=resource_id,
        )

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=WRITE_ONLY_AUTH_INFO,
        description="Deletes an agency",
        responses=create_response_dictionary("Agency successfully deleted."),
    )
    def delete(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            delete_agency, agency_id=resource_id, access_info=access_info
        )

