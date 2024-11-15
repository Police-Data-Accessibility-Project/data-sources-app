"""Integration tests for /reset-password endpoint."""
from datetime import datetime, timedelta
from http import HTTPStatus
import uuid

from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.enums import Relations
from tests.conftest import dev_db_client
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.TestUserSetup import TestUserSetup
from tests.helper_scripts.helper_functions import (
    request_reset_password_api, get_authorization_header,
)
from conftest import test_data_creator_flask, monkeysession

def test_reset_password_post(test_data_creator_flask: TestDataCreatorFlask, dev_db_client, mocker):
    """
    Test that POST call to /reset-password endpoint successfully resets the user's password, and verifies the new password digest is distinct from the old one in the database
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    user_info = tus.user_info

    def login(
        password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK
    ):
        tdc.request_validator.login(
            email=user_info.email,
            password=password,
            expected_response_status=expected_response_status,
        )

    # User should be able to log in with the old password
    login(user_info.password)

    old_password_digest = dev_db_client.get_user_info(user_info.email).password_digest

    token = request_reset_password_api(tdc.flask_client, mocker, user_info)

    # Token should be valid
    tdc.request_validator.reset_token_validation(
        token=token,
        expected_response_status=HTTPStatus.OK,
        expected_json_content={"message": "Token is valid"},
    )

    # But token should not work other endpoints which take bearer tokens
    tdc.request_validator.get(
        endpoint=DATA_SOURCES_BASE_ENDPOINT,
        headers=get_authorization_header(scheme="Bearer", token=token),
        expected_response_status=HTTPStatus.UNPROCESSABLE_ENTITY
    )

    new_password = str(uuid.uuid4())

    tdc.request_validator.reset_password(
        token=token,
        password=new_password,
    )

    new_password_digest = dev_db_client.get_user_info(user_info.email).password_digest
    assert (
        new_password_digest != old_password_digest
    ), "Old and new password digests should be distinct"

    # User should not be able to log in with the old password
    login(
        password=user_info.password,
        expected_response_status=HTTPStatus.UNAUTHORIZED
    )

    # User should be able to login with the new password
    login(
        password=new_password
    )

def test_reset_token_validation_invalid_token_unprocessable(
        test_data_creator_flask: TestDataCreatorFlask
):
    tdc = test_data_creator_flask

    # Test invalid on nonsense token
    token = str(uuid.uuid4())
    tdc.request_validator.reset_token_validation(
        token=token,
        expected_response_status=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

def test_reset_token_validation_invalid_token_expired(
    test_data_creator_flask: TestDataCreatorFlask,
    mocker
):
    tdc = test_data_creator_flask

    tus: TestUserSetup = tdc.standard_user()

    # Test invalid on expired token
    token = request_reset_password_api(tdc.flask_client, mocker, tus.user_info)

    # Check it's valid initially
    tdc.request_validator.reset_token_validation(
        token=token,
        expected_response_status=HTTPStatus.OK,
        expected_json_content={"message": "Token is valid"},
    )

    # Go into database and manually expire token
    decoded_token = SimpleJWT.decode(token=token, purpose=JWTPurpose.PASSWORD_RESET)
    tdc.db_client._update_entry_in_table(
        table_name=Relations.RESET_TOKENS.value,
        entry_id=decoded_token.sub["token"],
        column_edit_mappings={
            "create_date": datetime.now() - timedelta(minutes=15)
        },
        id_column_name="token",
    )

    tdc.request_validator.reset_token_validation(
        token=token,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": "Token is expired."},
    )
