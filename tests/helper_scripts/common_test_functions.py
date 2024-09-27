"""
Functions commonly used in testing and asserting results
"""

from http import HTTPStatus

import pytest
from flask_jwt_extended import decode_token

from database_client.constants import PAGE_SIZE
from database_client.database_client import DatabaseClient
from middleware.schema_and_dto_logic.response_schemas import EntryDataResponseSchema
from tests.helper_scripts.helper_classes.IntegrationTestSetup import IntegrationTestSetup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status, assert_is_oauth_redirect_link


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



def test_delete_endpoint(
    add_entry_db_client_method: callable,
    id_column_name: str,
    endpoint_name: str,
    **add_entry_args
):
    """
    Tests that a given delete endpoint properly deletes data
    :return:
    """

    # Create user with elevated permissions


    # Add entry


    # Delete entry with call to endpoint


    # Check that entry no longer exists


    pytest.fail()

def test_get_by_id_endpoint(
    get_by_id_db_client_method: callable
):
    """
    Tests that a given get_by_id endpoint properly retrieves data
    :return:
    """
    pytest.fail()


def call_and_validate_get_by_id_endpoint(
    its: IntegrationTestSetup,
    id_name: str,
    base_endpoint: str,
    expected_value_key: str,
    expected_value: str
):

    json_data = run_and_validate_request(
        flask_client=its.flask_client,
        http_method="get",
        endpoint=f"{base_endpoint}/{id_name}",
        headers=its.tus.jwt_authorization_header,
        expected_schema=EntryDataResponseSchema
    )

    assert expected_value_key in json_data["data"]
    assert json_data["data"][expected_value_key] == expected_value

    return json_data


