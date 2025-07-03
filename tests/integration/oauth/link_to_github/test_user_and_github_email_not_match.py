import uuid
from http import HTTPStatus

from endpoints.schema_config.instantiations.auth.github.link import (
    AuthGithubLinkEndpointSchemaConfig,
)
from tests.helper_scripts.constants import GITHUB_OAUTH_LINK_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.integration.oauth.helpers import setup_github_mocks


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
        expected_schema=AuthGithubLinkEndpointSchemaConfig.primary_output_schema,
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
