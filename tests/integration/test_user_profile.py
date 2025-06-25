from http import HTTPStatus
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from tests.helper_scripts.complex_test_data_creation_functions import (
    create_test_data_request,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_user_profile_data_requests(test_data_creator_flask: TestDataCreatorFlask):

    tdc = test_data_creator_flask

    # Create test user
    tus = tdc.standard_user()

    # Call user profile data requests endpoint and confirm it returns no results
    tdc.request_validator.get_user_profile_data_requests(
        headers=tus.jwt_authorization_header,
        expected_json_content={"metadata": {"count": 0}, "data": [], "message": ""},
    )

    # Add a data request
    tdr = create_test_data_request(tdc.flask_client, tus.jwt_authorization_header)

    # Call user profile data requests endpoint and confirm it returns results
    json_response = tdc.request_validator.get_user_profile_data_requests(
        headers=tus.jwt_authorization_header,
    )

    assert len(json_response["data"]) == 1
    assert json_response["data"][0]["id"] == int(tdr.id)
    assert json_response["data"][0]["submission_notes"] == tdr.submission_notes

    # Create additional data requests and confirm they are returned
    create_test_data_request(tdc.flask_client, tus.jwt_authorization_header)
    create_test_data_request(tdc.flask_client, tus.jwt_authorization_header)

    json_response = tdc.request_validator.get_user_profile_data_requests(
        headers=tus.jwt_authorization_header,
    )

    assert len(json_response["data"]) == 3

    # Test limit

    json_response = tdc.request_validator.get_user_profile_data_requests(
        headers=tus.jwt_authorization_header,
        limit=2,
    )

    assert len(json_response["data"]) == 2


def test_user_profile_get_by_id(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    # Create test user
    tus = tdc.standard_user()

    # Create a recent search
    tdc.request_validator.search(
        headers=tus.api_authorization_header,
        location_id=tdc.db_client.get_location_id(
            where_mappings={
                "state_name": "Pennsylvania",
                "county_name": None,
                "locality_name": None,
            }
        ),
    )

    # Have the user follow a search
    tdc.request_validator.follow_search(
        headers=tus.jwt_authorization_header,
        location_id=tdc.db_client.get_location_id(
            where_mappings={
                "state_name": "California",
                "county_name": None,
                "locality_name": None,
            }
        ),
    )

    # Have the user create a data request
    data_request_id = tdc.data_request(user_tus=tus).id

    # Assign the user a permission
    tdc.add_permission(
        user_email=tus.user_info.email,
        permission=PermissionsEnum.READ_ALL_USER_INFO,
    )

    # Link the user to a fictional github account
    github_user_id = tdc.tdcdb.link_fake_github_to_user(user_id=tus.user_info.user_id)

    # Call user profile endpoint and confirm it returns results
    json_response = tdc.request_validator.get_user_by_id(
        headers=tus.jwt_authorization_header,
        user_id=tus.user_info.user_id,
    )

    data = json_response["data"]

    assert data["email"] == tus.user_info.email
    assert data["external_accounts"]["github"] == str(github_user_id)
    assert data["recent_searches"]["data"][0]["state_name"] == "Pennsylvania"
    assert data["followed_searches"]["data"][0]["state_name"] == "California"
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
    tdc.request_validator.get_user_by_id(
        headers=tus_2.jwt_authorization_header,
        user_id=tus.user_info.user_id,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=MessageSchema(),
    )
