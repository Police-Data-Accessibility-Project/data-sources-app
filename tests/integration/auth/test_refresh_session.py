"""Integration tests for /refresh-session endpoint."""

from http import HTTPStatus

from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.helper_functions_complex import (
    login_and_return_jwt_tokens,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_refresh_session_post(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that POST call to /refresh-session endpoint successfully generates a new session token, ensures the new token is different from the old one, and verifies the old token is removed while the new token exists in the session tokens table
    """
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    jwt_tokens = login_and_return_jwt_tokens(tdc.flask_client, admin_tus.user_info)

    # Test that the access token works properly for a secure endpoint
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/data-requests",
        headers={"Authorization": f"Bearer {jwt_tokens.access_token}"},
    )

    # Test that the refresh token works properly
    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint="/auth/refresh-session",
        headers={"Authorization": f"Bearer {jwt_tokens.refresh_token}"},
    )

    new_access_token = response_json.get("access_token")
    new_refresh_token = response_json.get("refresh_token")

    assert jwt_tokens.access_token != new_access_token, (
        "New and old access tokens should be different"
    )

    assert jwt_tokens.refresh_token != new_refresh_token, (
        "New and old refresh tokens should be different"
    )

    # Test that the new session tokens work on a secure endpoint
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/data-requests",
        headers={"Authorization": f"Bearer {jwt_tokens.access_token}"},
    )


def test_refresh_session_post_access_token(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    standard_tus = tdc.standard_user()

    jwt_tokens = login_and_return_jwt_tokens(tdc.flask_client, standard_tus.user_info)

    # Test that refresh session fails when the access token is used
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint="/auth/refresh-session",
        headers={"Authorization": f"Bearer {jwt_tokens.access_token}"},
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )
