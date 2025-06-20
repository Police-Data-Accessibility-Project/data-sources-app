import uuid
from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose
from tests.helper_scripts.constants import (
    GITHUB_OAUTH_LINK_ENDPOINT,
    GITHUB_OAUTH_LOGIN_ENDPOINT,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


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
