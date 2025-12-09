from http import HTTPStatus

from db.models.implementations.core.user.permission import UserPermission
from middleware.enums import RecordTypesEnum
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_user_profile_get_by_id(
    test_data_creator_flask: TestDataCreatorFlask, pennsylvania_id, california_id
):
    tdc = test_data_creator_flask

    # Create test user
    tus = tdc.standard_user()

    # Create a recent search
    tdc.request_validator.search(
        headers=tus.api_authorization_header,
        location_id=pennsylvania_id,
    )

    # Create another recent search with no location
    tdc.request_validator.search(
        headers=tus.api_authorization_header,
        record_types=[RecordTypesEnum.BOOKING_REPORTS],
    )

    # Have the user follow a search
    tdc.request_validator.follow_search(
        headers=tus.jwt_authorization_header,
        location_id=california_id,
    )

    # Have the user create a data request
    data_request_id = tdc.data_request(user_id=tus.user_id).id

    # Assign the user a permission
    permission = UserPermission(
        user_id=tus.user_id,
        permission_id=1,
    )
    tdc.tdcdb.db_client.add(permission)

    # Link the user to a fictional github account
    github_user_id = tdc.tdcdb.link_fake_github_to_user(user_id=tus.user_info.user_id)

    # Call user profile endpoint and confirm it returns results
    json_response = tdc.request_validator.get_user_by_id(
        headers=tus.jwt_authorization_header,
        user_id=tus.user_id,
    )

    data = json_response["data"]

    assert data["email"] == tus.user_info.email
    assert data["external_accounts"]["github"] == str(github_user_id)
    assert data["recent_searches"]["data"][0]["state_name"] == "Pennsylvania"
    assert data["followed_searches"]["data"][0]["state_name"] == "California"
    assert data["data_requests"]["data"][0]["id"] == int(data_request_id)
    assert len(data["permissions"]) == 1

    # Test that admin can also get this user's information
    json_response_admin = tdc.request_validator.get_user_by_id(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        user_id=tus.user_id,
    )
    assert json_response_admin == json_response
    # Test that other non-admin users cannot get this user's information

    tus_2 = tdc.standard_user()
    tdc.request_validator.get_user_by_id(
        headers=tus_2.jwt_authorization_header,
        user_id=tus.user_id,
        expected_response_status=HTTPStatus.FORBIDDEN,
        expected_schema=MessageSchema(),
    )
