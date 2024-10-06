from middleware.schema_and_dto_logic.primary_resource_schemas.data_requests import (
    GetManyDataRequestsSchema,
)
from resources.UserProfile import USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL
from tests.conftest import flask_client_with_db
from tests.helper_scripts.common_test_data import create_test_data_request
from tests.helper_scripts.helper_functions import create_test_user_setup
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_user_profile_data_requests(flask_client_with_db):

    # Create test user
    tus = create_test_user_setup(flask_client_with_db)

    # Call user profile data requests endpoint and confirm it returns no results
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL}?page=1",
        headers=tus.jwt_authorization_header,
        expected_json_content={"count": 0, "data": [], "message": ""},
        expected_schema=GetManyDataRequestsSchema(exclude=["data.internal_notes"]),
    )

    # Add a data request
    tdr = create_test_data_request(flask_client_with_db, tus.jwt_authorization_header)

    # Call user profile data requests endpoint and confirm it returns results
    json_response = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{USER_PROFILE_DATA_REQUEST_ENDPOINT_FULL}?page=1",
        headers=tus.jwt_authorization_header,
        expected_schema=GetManyDataRequestsSchema(exclude=["data.internal_notes"]),
    )
    assert len(json_response["data"]) == 1
    assert json_response["data"][0]["id"] == int(tdr.id)
    assert json_response["data"][0]["submission_notes"] == tdr.submission_notes
