"""
Class based means to run and validate requests
"""
from http import HTTPStatus
from typing import Optional, Type, Union

from flask.testing import FlaskClient
from marshmallow import Schema

from middleware.util import update_if_not_none
from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.helper_functions import get_authorization_header, add_query_params
from tests.helper_scripts.run_and_validate_request import http_methods, run_and_validate_request
from utilities.enums import RecordCategories


class RequestValidator:

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client

    def post(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def get(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="get",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def put(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def delete(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="delete",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    # Below are shorthands for common requests

    def login(self, email: str, password: str, expected_response_status: HTTPStatus = HTTPStatus.OK):
        return self.post(
            endpoint="/api/login",
            json={"email": email, "password": password},
            expected_response_status=expected_response_status
        )

    def reset_password(
            self,
            token: str,
            password: str,
            expected_response_status: HTTPStatus = HTTPStatus.OK
    ):
        return self.post(
            endpoint="/api/reset-password",
            headers=get_authorization_header(scheme="Bearer", token=token),
            json={"password": password},
            expected_response_status=expected_response_status
        )

    def request_reset_password(
            self,
            email: str,
            mocker,
            expected_response_status: HTTPStatus = HTTPStatus.OK):
        mock = mocker.patch(
            "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
        )
        response = self.post(
            endpoint="/api/request-reset-password",
            json={"email": email},
            expected_response_status=expected_response_status
        )
        return mock.call_args[1]["token"]

    def reset_token_validation(
        self,
        token: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None
    ):
        return self.post(
            endpoint="/api/reset-token-validation",
            headers=get_authorization_header(scheme="Bearer", token=token),
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content
        )

    def get_permissions(
        self,
        user_email: str,
        headers: dict,
        expected_json_content: Optional[dict] = None
    ):
        endpoint = f"/auth/permissions?user_email={user_email}"
        return self.get(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content
        )

    def update_permissions(
        self,
        user_email: str,
        headers: dict,
        action: str,
        permission: str,
    ):
        endpoint = f"/auth/permissions?user_email={user_email}"
        return self.put(
            endpoint=endpoint,
            headers=headers,
            json={"action": action, "permission": permission},
        )

    def search(
        self,
        headers: dict,
        state: str,
        record_categories: Optional[list[RecordCategories]] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
    ):
        endpoint_base = "/search/search-location-and-record-type"
        query_params = self._get_search_query_params(
            county=county,
            locality=locality,
            record_categories=record_categories,
            state=state
        )
        endpoint = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        return self.get(
            endpoint=endpoint,
            headers=headers,
            expected_schema=SchemaConfigs.SEARCH_LOCATION_AND_RECORD_TYPE_GET.value.primary_output_schema,
        )

    @staticmethod
    def _get_search_query_params(county, locality, record_categories, state):
        query_params = {
            "state": state,
        }
        if record_categories is not None:
            query_params["record_categories"] = ",".join([rc.value for rc in record_categories])
        update_if_not_none(
            dict_to_update=query_params,
            secondary_dict={
                "county": county,
                "locality": locality,
            },
        )
        return query_params

    def follow_search(
        self,
        headers: dict,
        state: str,
        record_categories: Optional[list[RecordCategories]] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
        expected_json_content: Optional[dict] = None,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        endpoint_base = "/api/search/follow"
        query_params = self._get_search_query_params(
            county=county,
            locality=locality,
            record_categories=record_categories,
            state=state
        )
        endpoint = add_query_params(
            url=endpoint_base,
            params=query_params,
        )
        return self.post(
            endpoint=endpoint,
            headers=headers,
            expected_json_content=expected_json_content,
            expected_response_status=expected_response_status,
            expected_schema=SchemaConfigs.SEARCH_FOLLOW_POST.value.primary_output_schema,
        )

    def get_user_by_id(
        self,
        headers: dict,
        user_id: int,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_schema=SchemaConfigs.USER_PROFILE_GET.value.primary_output_schema
    ):
        return self.get(
            endpoint=f"/api/user/{user_id}",
            headers=headers,
            expected_schema=expected_schema,
            expected_response_status=expected_response_status
        )