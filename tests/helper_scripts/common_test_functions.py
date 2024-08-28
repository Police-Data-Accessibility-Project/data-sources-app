"""
Functions commonly used in testing and asserting results
"""

from http import HTTPStatus

from flask_jwt_extended import decode_token

from database_client.constants import PAGE_SIZE
from database_client.database_client import DatabaseClient


def has_expected_keys(result_keys: list, expected_keys: list) -> bool:
    """
    Check that given result includes expected keys.

    :param result:
    :param expected_keys:
    :return: True if has expected keys, false otherwise
    """
    return not set(expected_keys).difference(result_keys)


def check_response_status(response, status_code):
    assert (
        response.status_code == status_code
    ), f"Expected status code {status_code}, got {response.status_code}: {response.text}"


def assert_is_oauth_redirect_link(text: str):
    assert "https://github.com/login/oauth/authorize?response_type=code" in text, (
        "Expected OAuth authorize link, got: " + text
    )


def assert_expected_pre_callback_response(response):
    check_response_status(response, HTTPStatus.FOUND)
    response_text = response.text
    assert_is_oauth_redirect_link(response_text)


def assert_api_key_exists_for_email(db_client: DatabaseClient, email: str, api_key):
    user_info = db_client.get_user_info(email)
    assert user_info.api_key == api_key


def assert_jwt_token_matches_user_email(email: str, jwt_token: str):
    decoded_token = decode_token(jwt_token)
    assert email == decoded_token["sub"]

def assert_expected_get_many_result(response_json: dict, expected_non_null_columns: list[str]):
    data = response_json["data"]
    assert 0 < len(data) <= PAGE_SIZE
    assert isinstance(data[0], dict)
    for column in expected_non_null_columns:
        assert column in data[0]
        assert data[0][column] is not None
