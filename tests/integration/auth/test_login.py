"""Integration tests for /login endpoint"""

from http import HTTPStatus

from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.common_asserts import (
    assert_jwt_token_matches_user_email,
)


def test_login_post(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    user_info = tus.user_info
    # Create user
    access_token = tdc.request_validator.login(
        email=user_info.email,
        password=user_info.password,
    )["access_token"]

    assert_jwt_token_matches_user_email(
        email=user_info.email,
        jwt_token=access_token,
    )


def test_login_post_user_not_exists(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    user_info = tus.user_info
    # Create user
    tdc.request_validator.login(
        email="gibberish",
        password=user_info.password,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )


def test_login_post_invalid_password(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token, and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    user_info = tus.user_info

    tdc.request_validator.login(
        email=user_info.email,
        password="gibberish",
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )
