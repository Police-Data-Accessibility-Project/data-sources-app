from http import HTTPStatus
from typing import Optional, Type, Union, Literal, TextIO

from flask.testing import FlaskClient
from marshmallow import Schema

from tests.helper_scripts.helper_functions_simple import add_query_params
from tests.helper_scripts.common_asserts import assert_response_status

http_methods = Literal["get", "post", "put", "patch", "delete"]


def run_and_validate_request(
    flask_client: FlaskClient,
    http_method: http_methods,
    endpoint: str,
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_json_content: Optional[dict] = None,
    expected_schema: Optional[Union[Type[Schema], Schema]] = None,
    query_parameters: Optional[dict] = None,
    file: Optional[TextIO] = None,
    return_json: bool = True,
    **request_kwargs,
):
    """
    Run a request and validate the response.
    :param flask_client: The flask test client
    :param http_method: The http method to use
    :param endpoint: The endpoint to send the request to
    :param expected_response_status: The expected status code of the response
    :param expected_json_content: The expected json content of the response
    :param expected_schema: An optional Marshmallow schema to validate the response against
    :param query_parameters: Query parameters, if any, to add to the endpoint
    :param file: The file to send, if any
    :param return_json: Whether to return the json content of the response, or the raw response data
    :param request_kwargs: Additional keyword arguments to add to the request
    :return: The json content of the response
    """
    if query_parameters is not None:
        endpoint = add_query_params(endpoint, query_parameters)

    if file is not None:
        # Check file is open
        if file.closed is True:
            # Open file
            file = open(file.name, "rb")
        assert file.closed is False, "File must be opened before sending request."
        response = flask_client.open(
            endpoint,
            method=http_method,
            data={"file": file},
            content_type="multipart/form-data",
            **request_kwargs,
        )
    else:
        response = flask_client.open(endpoint, method=http_method, **request_kwargs)
    assert_response_status(response, expected_response_status.value)

    if not return_json:
        return response.data

    # All of our requests should return some json message providing information.
    assert response.json is not None

    # But we can also test to see if the json content is what we expect
    if expected_json_content is not None:
        try:
            assert response.json == expected_json_content
        except AssertionError:
            raise AssertionError(
                f"Expected {expected_json_content} but got {response.json}"
            )

    if expected_schema is not None:
        if not isinstance(expected_schema, Schema):
            expected_schema = expected_schema()
        expected_schema.load(response.json)

    return response.json
