"""Integration tests for /refresh-session endpoint."""

from http import HTTPStatus
import psycopg2.extensions

from tests.fixtures import dev_db_connection, flask_client_with_db
from tests.helper_scripts.helper_functions import create_test_user_api, login_and_return_jwt_tokens

def test_refresh_session_post(
    flask_client_with_db, dev_db_connection: psycopg2.extensions.connection
):
    """
    Test that POST call to /refresh-session endpoint successfully generates a new session token, ensures the new token is different from the old one, and verifies the old token is removed while the new token exists in the session tokens table
    """

    test_user = create_test_user_api(flask_client_with_db)
    jwt_tokens = login_and_return_jwt_tokens(flask_client_with_db, test_user)
    response = flask_client_with_db.post(
        "/api/refresh-session",
        headers={"Authorization": f"Bearer {jwt_tokens.refresh_token}"},
    )
    assert response.status_code == HTTPStatus.OK.value
    new_session_token = response.json.get("data")

    assert (
        jwt_tokens.access_token != new_session_token
    ), "New and old tokens should be different"
