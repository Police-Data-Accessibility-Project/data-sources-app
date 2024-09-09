from http import HTTPStatus
from typing import Optional

from flask.testing import FlaskClient

from tests.helper_scripts.simple_result_validators import check_response_status


def run_and_validate_request(
    flask_client: FlaskClient,
    http_method: str,
    endpoint: str,
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_json_content: Optional[dict] = None,
    **request_kwargs,
):
    response = flask_client.open(endpoint, method=http_method, **request_kwargs)
    check_response_status(response, expected_response_status.value)

    # All of our requests should return some json message providing information.
    assert response.json is not None

    # But we can also test to see if the json content is what we expect
    if expected_json_content is not None:
        assert response.json == expected_json_content, f"Expected {expected_json_content} but got {response.json}"

    return response.json
