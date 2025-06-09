import uuid
from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from flask.testing import FlaskClient

from tests.conftest import test_data_creator_flask
from middleware.SimpleJWT import SimpleJWT, JWTPurpose
from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from endpoints.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import (
    get_random_number_for_testing,
    get_test_name,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.common_asserts import (
    assert_jwt_token_matches_user_email,
)
from tests.helper_scripts.constants import (
    GITHUB_OAUTH_LOGIN_ENDPOINT,
    GITHUB_OAUTH_LINK_ENDPOINT,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request

GITHUB_OATH_LOGIC_PATCH_ROOT = "middleware.primary_resource_logic.github_oauth"


def login_with_github(client: FlaskClient, access_token: str) -> str:
    data = run_and_validate_request(
        flask_client=client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LOGIN_ENDPOINT,
        expected_schema=SchemaConfigs.AUTH_GITHUB_LOGIN.value.primary_output_schema,
        json={"gh_access_token": access_token},
    )
    return data["access_token"]


def setup_github_mocks(user_email: str, monkeypatch):
    mock_access_token = uuid.uuid4().hex
    simple_jwt = SimpleJWT(
        sub=mock_access_token,
        exp=datetime.now(tz=timezone.utc).timestamp()
        + timedelta(minutes=5).total_seconds(),
        purpose=JWTPurpose.GITHUB_ACCESS_TOKEN,
    )
    mock_external_user_id = get_random_number_for_testing()

    # Mock the part that ingests the Github Access Token and returns relevant info
    def mock_get_github_user_id(token: str) -> int:
        assert token == mock_access_token
        return mock_external_user_id

    def mock_get_github_user_email(token: str) -> str:
        assert token == mock_access_token
        return user_email

    monkeypatch.setattr(
        f"{GITHUB_OATH_LOGIC_PATCH_ROOT}.get_github_user_id", mock_get_github_user_id
    )

    monkeypatch.setattr(
        f"{GITHUB_OATH_LOGIC_PATCH_ROOT}.get_github_user_email",
        mock_get_github_user_email,
    )

    return simple_jwt.encode()


def test_link_to_github_oauth(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    tdc = test_data_creator_flask
    # Create user
    tus = tdc.standard_user()
    access_token = setup_github_mocks(
        user_email=tus.user_info.email, monkeypatch=monkeypatch
    )

    # Call endpoint with mock access token
    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=SchemaConfigs.AUTH_GITHUB_LINK.value.primary_output_schema,
        json={"user_email": tus.user_info.email, "gh_access_token": access_token},
    )

    # After linking user, try logging in with GitHub to confirm functionality
    access_token = login_with_github(client=tdc.flask_client, access_token=access_token)

    # Confirm api_key received, when hashed, matches user's api_key in database
    assert_jwt_token_matches_user_email(
        email=tus.user_info.email,
        jwt_token=access_token,
    )


def test_link_to_github_oauth_user_email_not_in_db(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=SchemaConfigs.AUTH_GITHUB_LINK.value.primary_output_schema,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        json={
            "user_email": get_test_name(),  # Create email guaranteed to not exist in database
            "gh_access_token": uuid.uuid4().hex,  # This logic should not be called until we validate the user is present
        },
    )

    assert data["message"] == "Email provided not associated with any user."


def test_link_to_github_oauth_user_and_github_email_not_match(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    tdc = test_data_creator_flask

    tus = tdc.standard_user()

    # Setup GitHub mocks with different email
    access_token = setup_github_mocks(
        user_email=uuid.uuid4().hex, monkeypatch=monkeypatch
    )

    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=SchemaConfigs.AUTH_GITHUB_LINK.value.primary_output_schema,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        json={
            "user_email": tus.user_info.email,
            "gh_access_token": access_token,  # This logic should not be called until we validate the user is present
        },
    )

    assert (
        data["message"]
        == "Email provided does not match primary email in GitHub account."
    )


def test_login_with_github_user_not_exists(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    # Call the login with GitHub endpoint for a user that does not exist
    # The user should be created
    email = get_test_name()

    gh_access_token = setup_github_mocks(user_email=email, monkeypatch=monkeypatch)
    tdc = test_data_creator_flask

    # Call endpoint with mock access token
    # Check that results obtained in expected schema
    access_token = login_with_github(
        client=tdc.flask_client, access_token=gh_access_token
    )

    # Confirm access token received, when hashed, matches user's access token in database
    assert_jwt_token_matches_user_email(
        email=email,
        jwt_token=access_token,
    )


def test_github_oauth_token_expired(
    test_data_creator_flask: TestDataCreatorFlask, monkeypatch
):
    tdc = test_data_creator_flask
    # Create user
    tus = tdc.standard_user()
    mock_access_token = uuid.uuid4().hex
    simple_jwt = SimpleJWT(
        sub=mock_access_token,
        exp=datetime.now(tz=timezone.utc).timestamp()
        - timedelta(minutes=5).total_seconds(),
        purpose=JWTPurpose.GITHUB_ACCESS_TOKEN,
    )
    encoded_jwt = simple_jwt.encode()

    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=MessageSchema(),
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_json_content={"message": "Access token has expired."},
        json={
            "user_email": tus.user_info.email,
            "gh_access_token": encoded_jwt,  # This logic should not be called until we validate the user is present
        },
    )

    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LOGIN_ENDPOINT,
        expected_schema=MessageSchema(),
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        expected_json_content={"message": "Access token has expired."},
        json={"gh_access_token": encoded_jwt},
    )
