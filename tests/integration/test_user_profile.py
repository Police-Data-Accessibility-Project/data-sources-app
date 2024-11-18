from http import HTTPStatus

import pytest

from middleware.enums import PermissionsEnum
from middleware.schema_and_dto_logic.common_response_schemas import MessageSchema
from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests_advanced_schemas import (
    GetManyDataRequestsResponseSchema,
)
from resources.UserProfile import USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL
from tests.conftest import flask_client_with_db
from tests.helper_scripts.complex_test_data_creation_functions import create_test_data_request
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask
from tests.helper_scripts.helper_functions import create_test_user_setup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from conftest import test_data_creator_flask, monkeysession

def test_user_profile_data_requests(flask_client_with_db):

    # Create test user
    tus = create_test_user_setup(flask_client_with_db)

    # Call user profile data requests endpoint and confirm it returns no results
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL}?page=1",
        headers=tus.jwt_authorization_header,
        expected_json_content={"metadata": {"count": 0}, "data": [], "message": ""},
        expected_schema=GetManyDataRequestsResponseSchema(
            exclude=["data.internal_notes"]
        ),
    )

    # Add a data request
    tdr = create_test_data_request(flask_client_with_db, tus.jwt_authorization_header)

    # Call user profile data requests endpoint and confirm it returns results
    json_response = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL}?page=1",
        headers=tus.jwt_authorization_header,
        expected_schema=GetManyDataRequestsResponseSchema(
            exclude=["data.internal_notes"]
        ),
    )
    assert len(json_response["data"]) == 1
    assert json_response["data"][0]["id"] == int(tdr.id)
    assert json_response["data"][0]["submission_notes"] == tdr.submission_notes

def test_user_profile_get_by_id(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    # Create test user
    tus = tdc.standard_user()

    # Create a recent search
    tdc.request_validator.search(
        headers=tus.api_authorization_header,
        state="Pennsylvania",
    )

    # Have the user follow a search
    tdc.request_validator.follow_search(
        headers=tus.jwt_authorization_header,
        state="California",
    )

    # Have the user create a data request
    data_request_id = tdc.data_request(user_tus=tus).id

    # Assign the user a permission
    tdc.add_permission(
        user_email=tus.user_info.email,
        permission=PermissionsEnum.READ_ALL_USER_INFO,
    )

    # Link the user to a fictional github account
    github_user_id = tdc.tdcdb.link_fake_github_to_user(
        user_id=tus.user_info.user_id
    )

    # Call user profile endpoint and confirm it returns results
    json_response = tdc.request_validator.get_user_by_id(
        headers=tus.jwt_authorization_header,
        user_id=tus.user_info.user_id,
    )

    data = json_response["data"]

    assert data["email"] == tus.user_info.email
    assert data["external_accounts"]["github"] == str(github_user_id)
    assert data["recent_searches"]["data"][0]["state_iso"] == "PA"
    assert data["followed_searches"]["data"][0]["state"] == "California"
    assert data["data_requests"]["data"][0]["id"] == int(data_request_id)
    assert data["permissions"] == [PermissionsEnum.READ_ALL_USER_INFO.value]

    # Test that admin can also get this user's information
    json_response_admin = tdc.request_validator.get_user_by_id(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        user_id=tus.user_info.user_id,
    )
    assert json_response_admin == json_response
    # Test that other non-admin users cannot get this user's information

    tus_2 = tdc.standard_user()
    json_response_2 = tdc.request_validator.get_user_by_id(
        headers=tus_2.jwt_authorization_header,
        user_id=tus.user_info.user_id,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=MessageSchema()
    )
