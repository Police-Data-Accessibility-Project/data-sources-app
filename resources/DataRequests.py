from http import HTTPStatus

from flask import Response

from middleware.access_logic import AccessInfo
from middleware.data_requests import (
    create_data_request_wrapper,
    get_data_requests_wrapper,
    delete_data_requests_wrapper,
    update_data_requests_wrapper,
    get_data_request_by_id_wrapper,
)
from middleware.dataclasses import EntryDataRequest
from middleware.decorators import (
    authentication_required,
)
from middleware.enums import PermissionsEnum, AccessTypeEnum
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from utilities.namespace import create_namespace, AppNamespaces
from utilities.populate_dto_with_request_content import (
    SourceMappingEnum,
    DTOPopulateParameters,
)

namespace_data_requests = create_namespace(AppNamespaces.DATA_REQUESTS)

# TODO: Create models for data requests to expect and return, and add to documentation


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
    )
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
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
    @namespace_data_requests.response(HTTPStatus.OK, "Success; Data request updated")
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.FORBIDDEN, "Invalid permissions")
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    def put(self, data_request_id: str, access_info: AccessInfo) -> Response:
        """
        Update data request
        :return:
        """
        return self.run_endpoint(
            update_data_requests_wrapper,
            dto_populate_parameters=DTOPopulateParameters(
                dto_class=EntryDataRequest,
                source=SourceMappingEnum.JSON,
            ),
            data_request_id=data_request_id,
            access_info=access_info
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
    def delete(self, data_request_id: str, access_info: AccessInfo) -> Response:
        """
        Delete data request
        :return:
        """
        return self.run_endpoint(
            delete_data_requests_wrapper,
            data_request_id=data_request_id,
            access_info=access_info
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
    )
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    def get(self, access_info: AccessInfo) -> Response:
        """
        Retrieves data requests with optional filters
        For non-admins, data requests the user created will be returned first
        and will include additional columns to reflect ownership
        TODO: Check all these lines show up in swagger
        :return:
        """
        return self.run_endpoint(get_data_requests_wrapper, access_info=access_info)

    @handle_exceptions
    @authentication_required(
        allowed_access_methods=[AccessTypeEnum.JWT],
    )
    @namespace_data_requests.response(HTTPStatus.OK, "Success; Data request created")
    @namespace_data_requests.response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "Internal server error"
    )
    @namespace_data_requests.response(HTTPStatus.FORBIDDEN, "Invalid permissions")
    @namespace_data_requests.response(HTTPStatus.BAD_REQUEST, "Invalid API Key or JWT")
    def post(self, access_info: AccessInfo) -> Response:
        """
        Creates a new data request
        :return:
        """
        return self.run_endpoint(
            wrapper_function=create_data_request_wrapper,
            dto_populate_parameters=DTOPopulateParameters(
                dto_class=EntryDataRequest,
                source=SourceMappingEnum.JSON,
            ),
            access_info=access_info,
        )
