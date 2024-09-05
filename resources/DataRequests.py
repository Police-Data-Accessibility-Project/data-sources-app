from http import HTTPStatus

from flask import Response
from flask_restx import fields

from middleware.access_logic import AccessInfo
from middleware.column_permission_logic import create_column_permissions_string_table
from middleware.primary_resource_logic.data_requests import (
    create_data_request_wrapper,
    get_data_requests_wrapper,
    delete_data_request_wrapper,
    update_data_request_wrapper,
    get_data_request_by_id_wrapper,
)
from middleware.schema_and_dto_logic.common_schemas_and_dtos import (
    EntryDataRequestDTO,
)
from middleware.decorators import (
    authentication_required,
)
from middleware.enums import AccessTypeEnum, Relations
from middleware.schema_and_dto_logic.model_helpers_with_schemas import (
    create_entry_data_request_model,
    create_id_and_message_model,
    create_get_many_response_model,
    create_entry_data_response_model,
)
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from resources.resource_helpers import (
    add_jwt_or_api_key_header_arg,
)
from utilities.namespace import create_namespace, AppNamespaces

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)

# TODO: Create models for data requests to expect and return, and add to documentation

entry_data_requests_model = create_entry_data_request_model(namespace_data_requests)
entry_data_response_model = create_entry_data_response_model(namespace_data_requests)
data_requests_outer_model = create_get_many_response_model(namespace_data_requests)
id_and_message_model = create_id_and_message_model(namespace_data_requests)

data_requests_column_permissions = create_column_permissions_string_table(
    relation=Relations.DATA_REQUESTS.value
)

authorization_parser = namespace_data_requests.parser()
add_jwt_or_api_key_header_arg(authorization_parser)


@namespace_data_requests.route("/by-id/<data_request_id>")
@namespace_data_requests.param(
    name="data_request_id", description="The data request id", _in="path"
)
class DataRequestsById(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
    )
    @namespace_data_requests.response(
        HTTPStatus.OK,
        "Success; Data request retrieved",
        model=entry_data_response_model,
    )
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    @namespace_data_requests.doc(
        description=f"""
        Get data request by id
        
Columns returned are determinant upon the user's access level and/or relation to the data request
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        """
    )
    @namespace_data_requests.expect(authorization_parser, validate=True)
    def get(self, access_info: AccessInfo, data_request_id: str) -> Response:
        """
        Get data request by id
        :return:
        """
        return self.run_endpoint(
            get_data_request_by_id_wrapper,
            access_info=access_info,
            data_request_id=data_request_id,
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.expect(authorization_parser, entry_data_requests_model)
    @namespace_data_requests.response(HTTPStatus.OK, "Success; Data request updated")
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.FORBIDDEN, "Invalid permissions")
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    @namespace_data_requests.doc(
        description=f"""
        Updates data request
        
Columns allowed to be updated by the user is determinant upon the user's access level and/or relation to the data request:
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        
        """,
    )
    def put(self, data_request_id: str, access_info: AccessInfo) -> Response:
        """
        Update data request
        :return:
        """
        return self.run_endpoint(
            update_data_request_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            data_request_id=data_request_id,
            access_info=access_info,
        )

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.response(HTTPStatus.OK, "Success; Data request deleted")
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.FORBIDDEN, "Invalid permissions")
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    @namespace_data_requests.expect(authorization_parser, validate=True)
    def delete(self, data_request_id: str, access_info: AccessInfo) -> Response:
        """
        Delete data request
        """
        return self.run_endpoint(
            delete_data_request_wrapper,
            data_request_id=data_request_id,
            access_info=access_info,
        )


@namespace_data_requests.route("/")
class DataRequests(PsycopgResource):

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.API_KEY, AccessTypeEnum.JWT],
    )
    @namespace_data_requests.response(
        HTTPStatus.OK,
        "Success",
        model=data_requests_outer_model,
    )
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    @namespace_data_requests.doc(
        description=f"""
        Gets data requests with optional filters
        For non-admins, data requests the user created will be returned first
        and will include additional columns to reflect ownership
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        """,
    )
    @namespace_data_requests.expect(authorization_parser, validate=True)
    def get(self, access_info: AccessInfo) -> Response:
        return self.run_endpoint(get_data_requests_wrapper, access_info=access_info)

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.expect(authorization_parser, entry_data_requests_model)
    @namespace_data_requests.response(
        code=HTTPStatus.OK,
        description="Success; Data request created",
        model=id_and_message_model,
    )
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.FORBIDDEN, "Invalid permissions")
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    @namespace_data_requests.doc(
        description=f"""
        Creates a new data request
        
Columns permitted to be included by the user is determined by their level of access
        
## COLUMN PERMISSIONS
        
{data_requests_column_permissions}
        
        """,
    )
    def post(self, access_info: AccessInfo) -> Response:
        """
        Creates a new data request
        :return:
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_wrapper,
            dto_populate_parameters=EntryDataRequestDTO.get_dto_populate_parameters(),
            access_info=access_info,
        )
