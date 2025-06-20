import uuid
from datetime import datetime, timezone, timedelta

from flask.testing import FlaskClient

from endpoints.schema_config.instantiations.auth.github.login import (
    AuthGithubLoginEndpointSchemaConfig,
)
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose
from tests.helper_scripts.common_test_data import get_random_number_for_testing
from tests.helper_scripts.constants import GITHUB_OAUTH_LOGIN_ENDPOINT
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.integration.oauth.constants import GITHUB_OATH_LOGIC_PATCH_ROOT


def login_with_github(client: FlaskClient, access_token: str) -> str:
    data = run_and_validate_request(
        flask_client=client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LOGIN_ENDPOINT,
        expected_schema=AuthGithubLoginEndpointSchemaConfig.primary_output_schema,
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
