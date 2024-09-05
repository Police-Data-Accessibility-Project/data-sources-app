"""Integration tests for /reset-token-validation endpoint."""

from http import HTTPStatus

from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    request_reset_password_api,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.fixtures import dev_db_connection, flask_client_with_db


def test_reset_token_validation(flask_client_with_db, dev_db_connection, mocker):
    """
    Test that POST call to /reset-token-validation endpoint successfully validates the reset token and returns the correct message indicating token validity
    """
    user_info = create_test_user_api(flask_client_with_db)
    token = request_reset_password_api(flask_client_with_db, mocker, user_info)
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint="/api/reset-token-validation",
        json={"token": token},
        expected_json_content={"message": "Token is valid"},
    )
