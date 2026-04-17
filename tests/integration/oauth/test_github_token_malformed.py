from http import HTTPStatus

import pytest

from middleware.schema_and_dto.schemas.common.common_response_schemas import (
    MessageSchema,
)
from tests.helpers.constants import (
    GITHUB_OAUTH_LINK_ENDPOINT,
    GITHUB_OAUTH_LOGIN_ENDPOINT,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


@pytest.mark.parametrize(
    "malformed_token",
    [
        "not-a-jwt",  # no dots at all → PyJWT raises ValueError on rsplit
        "only.two",  # only one dot → DecodeError: Not enough segments
        "",  # empty string
    ],
)
def test_github_oauth_token_malformed_login(
    test_data_creator_flask: TestDataCreatorFlask, malformed_token: str
):
    """A malformed gh_access_token should return 401, not 500."""
    tdc = test_data_creator_flask

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LOGIN_ENDPOINT,
        expected_schema=MessageSchema(),
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        json={"gh_access_token": malformed_token},
    )


@pytest.mark.parametrize(
    "malformed_token",
    [
        "not-a-jwt",
        "only.two",
        "",
    ],
)
def test_github_oauth_token_malformed_link(
    test_data_creator_flask: TestDataCreatorFlask, malformed_token: str
):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=MessageSchema(),
        expected_response_status=HTTPStatus.UNAUTHORIZED,
        json={
            "user_email": tus.user_info.email,
            "gh_access_token": malformed_token,
        },
    )
