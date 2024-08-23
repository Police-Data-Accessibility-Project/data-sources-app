"""Integration tests for /api_key endpoint"""

from http import HTTPStatus

from database_client.database_client import DatabaseClient
from resources.ApiKey import API_KEY_ROUTE
from tests.fixtures import dev_db_connection, flask_client_with_db, dev_db_client
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    check_response_status,
    run_and_validate_request,
)


def test_api_key_post(flask_client_with_db, dev_db_client):
    """
    Test that GET call to /api_key endpoint successfully creates an API key and aligns it with the user's API key in the database
    """

    user_info = create_test_user_api(flask_client_with_db)

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=f"/auth{API_KEY_ROUTE}",
        json={"email": user_info.email, "password": user_info.password},
    )

    # Check that API key aligned with user
    new_user_info = dev_db_client.get_user_info(user_info.email)
    assert new_user_info.api_key == response_json.get(
        "api_key"
    ), "API key returned not aligned with user API key in database"
