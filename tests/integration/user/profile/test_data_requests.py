from tests.helpers.helper_classes.test_data_creator.flask import (
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
    tdr = tdc.data_request(user_id=tus.user_id)

    # Call user profile data requests endpoint and confirm it returns results
    json_response = tdc.request_validator.get_user_profile_data_requests(
        headers=tus.jwt_authorization_header,
    )

    assert len(json_response["data"]) == 1
    assert json_response["data"][0]["id"] == int(tdr.id)
    assert json_response["data"][0]["submission_notes"] == tdr.submission_notes

    # Create additional data requests and confirm they are returned
    tdc.data_request(user_id=tus.user_id)
    tdc.data_request(user_id=tus.user_id)

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
