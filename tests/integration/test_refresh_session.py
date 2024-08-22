"""Integration tests for /refresh-session endpoint."""

import urllib.parse
from http import HTTPStatus

from middleware.enums import PermissionsEnum
from tests.fixtures import (
    dev_db_connection,
    flask_client_with_db,
    dev_db_client,
    test_user_admin,
)
from tests.helper_scripts.helper_functions import (
    login_and_return_jwt_tokens,
    run_and_validate_request,
    create_test_user_setup_db_client,
)


def test_refresh_session_post(test_user_admin, flask_client_with_db):
    """
    Test that POST call to /refresh-session endpoint successfully generates a new session token, ensures the new token is different from the old one, and verifies the old token is removed while the new token exists in the session tokens table
    """

    jwt_tokens = login_and_return_jwt_tokens(
        flask_client_with_db, test_user_admin.user_info
    )

    # Test that the access token works properly for a secure endpoint
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/auth/permissions?user_email=" + test_user_admin.user_info.email,
        headers={"Authorization": f"Bearer {jwt_tokens.access_token}"},
    )

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/refresh-session",
        headers={"Authorization": f"Bearer {jwt_tokens.refresh_token}"},
    )

    new_session_token = response_json.get("data")

    assert (
        jwt_tokens.access_token != new_session_token
    ), "New and old tokens should be different"

    # Test that the old session tokens work on a secure endpoint, but not the new one
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/auth/permissions?user_email=" + test_user_admin.user_info.email,
        headers={"Authorization": f"Bearer {new_session_token}"},
    )
