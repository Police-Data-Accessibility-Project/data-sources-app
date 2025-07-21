from endpoints.schema_config.instantiations.auth.github.link import (
    AuthGithubLinkEndpointSchemaConfig,
)
from tests.helpers.asserts import assert_jwt_token_matches_user_email
from tests.helpers.constants import GITHUB_OAUTH_LINK_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request
from tests.integration.oauth.helpers import setup_github_mocks, login_with_github


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
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=AuthGithubLinkEndpointSchemaConfig.primary_output_schema,
        json={"user_email": tus.user_info.email, "gh_access_token": access_token},
    )

    # After linking user, try logging in with GitHub to confirm functionality
    access_token = login_with_github(client=tdc.flask_client, access_token=access_token)

    # Confirm api_key received, when hashed, matches user's api_key in database
    assert_jwt_token_matches_user_email(
        email=tus.user_info.email,
        jwt_token=access_token,
    )
