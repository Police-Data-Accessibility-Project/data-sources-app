"""
Functions commonly used in testing and asserting results
"""

from http import HTTPStatus

from flask import Response
from flask_jwt_extended import decode_token

from database_client.constants import PAGE_SIZE
from database_client.database_client import DatabaseClient
from tests.helper_scripts.constants import TEST_RESPONSE


def assert_api_key_exists_for_email(db_client: DatabaseClient, email: str, api_key):
    user_info = db_client.get_user_info(email)
    assert user_info.api_key == api_key


def assert_jwt_token_matches_user_email(email: str, jwt_token: str):
    decoded_token = decode_token(jwt_token)
    assert email == decoded_token["sub"]["user_email"]


def assert_expected_get_many_result(
    response_json: dict, expected_non_null_columns: list[str]
):
    data = response_json["data"]
    assert 0 < len(data) <= PAGE_SIZE
    assert isinstance(data[0], dict)
    for column in expected_non_null_columns:
        assert column in data[0]
        assert data[0][column] is not None


def assert_contains_key_value_pairs(
    dict_to_check: dict,
    key_value_pairs: dict,
):
    for key, value in key_value_pairs.items():
        assert key in dict_to_check, f"Expected {key} to be in {dict_to_check}"
        dict_value = dict_to_check[key]
        assert dict_value == value, f"Expected {key} to be {value}, was {dict_value}"


def assert_is_test_response(response):
    assert_response_status(response, TEST_RESPONSE.status_code)
    assert response.json == TEST_RESPONSE.response


def assert_response_status(response: Response, status_code):
    assert (
        response.status_code == status_code
    ), f"{response.request.base_url}: Expected status code {status_code}, got {response.status_code}: {response.text}"
