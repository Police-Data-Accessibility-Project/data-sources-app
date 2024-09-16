from flask import Response
from flask_restx import fields

from middleware.access_logic import AccessInfo, GET_AUTH_INFO, WRITE_ONLY_AUTH_INFO
from middleware.primary_resource_logic.agencies import (
    get_agencies,
    get_agency_by_id,
    create_agency,
    update_agency,
    delete_agency,
)
from middleware.column_permission_logic import create_column_permissions_string_table
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
    GetManyBaseSchema,
    GetManyBaseDTO,
    GetByIDBaseSchema,
    GetByIDBaseDTO,
)
from middleware.decorators import (
    authentication_required,
    endpoint_info,
)
from middleware.enums import AccessTypeEnum, PermissionsEnum, Relations
from middleware.schema_and_dto_logic.model_helpers_with_schemas import (
    create_entry_data_request_model,
    create_id_and_message_model,
    create_get_many_response_model,
    create_entry_data_response_model,
    CRUDModels,
)
from middleware.schema_and_dto_logic.non_dto_dataclasses import SchemaPopulateParameters
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
    add_jwt_header_arg,
    create_response_dictionary,
    column_permissions_description,
)
from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_agencies = create_namespace(
    AppNamespaces.AGENCIES,
)

models = CRUDModels(namespace_agencies)

page_parser = namespace_agencies.parser()
page_parser.add_argument(
    "page",
    type=int,
    required=True,
    location="path",
    help="The page number of results to return.",
    default=1,
)
add_jwt_or_api_key_header_arg(page_parser)

agencies_column_permissions = create_column_permissions_string_table(
    relation=Relations.AGENCIES.value
)


@namespace_agencies.route("")
@namespace_agencies.expect(page_parser)
class AgenciesByPage(PsycopgResource):
    """Represents a resource for fetching approved agency data from the database."""

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=GET_AUTH_INFO,
        description=column_permissions_description(
            head_description="Get a paginated list of approved agencies",
            sub_description="Columns returned are determined by the user's access level.",
            column_permissions_str_table=agencies_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Returns a paginated list of approved agencies.",
            success_model=models.get_many_response_model,
        ),
    )
    def get(self, access_info: AccessInfo) -> Response:
        """
        Retrieves a paginated list of approved agencies from the database.

        Returns:
        - dict: A dictionary containing the count of returned agencies and their data.
        """
        return self.run_endpoint(
            wrapper_function=get_agencies,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=GetManyBaseSchema,
                dto_class=GetManyBaseDTO,
            ),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=WRITE_ONLY_AUTH_INFO,
        input_model=models.entry_data_request_model,
        description=column_permissions_description(
            head_description="Create a new agency",
            sub_description="Columns permitted to be included by the user is determined by their level of access",
            column_permissions_str_table=agencies_column_permissions,
        ),
        responses=create_response_dictionary(
            success_message="Returns the id of the newly created agency.",
            success_model=models.id_and_message_model,
        ),
    )
    def post(self, access_info: AccessInfo):
        return self.run_endpoint(
            wrapper_function=create_agency,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            access_info=access_info,
        )
        pass


@namespace_agencies.route("/<resource_id>")
class AgenciesById(PsycopgResource):

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=GET_AUTH_INFO,
        description=column_permissions_description(
            head_description="Get an agency by id",
            sub_description="Columns returned are determined by the user's access level.",
            column_permissions_str_table=agencies_column_permissions,
        ),
        responses=create_response_dictionary(
            "Returns agency.", models.entry_data_response_model
        ),
    )
    def get(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            wrapper_function=get_agency_by_id,
            schema_populate_parameters=SchemaPopulateParameters(
                schema_class=GetByIDBaseSchema,
                dto_class=GetByIDBaseDTO,
            ),
            access_info=access_info,
        )

    @endpoint_info(
        namespace=namespace_agencies,
        auth_info=WRITE_ONLY_AUTH_INFO,
        input_model=models.entry_data_request_model,
        description=column_permissions_description(
            head_description="Updates an agency",
            sub_description="Columns allowed to be updated by the user is determined by their level of access",
            column_permissions_str_table=agencies_column_permissions,
        ),
        responses=create_response_dictionary("Agency successfully updated."),
    )
    def put(self, resource_id: str, access_info: AccessInfo) -> Response:
        return self.run_endpoint(
            update_agency,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
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
