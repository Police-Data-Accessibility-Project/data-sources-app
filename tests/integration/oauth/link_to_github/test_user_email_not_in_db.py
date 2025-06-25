import uuid
from http import HTTPStatus

from endpoints.schema_config.instantiations.auth.github.link import (
    AuthGithubLinkEndpointSchemaConfig,
)
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import GITHUB_OAUTH_LINK_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_link_to_github_oauth_user_email_not_in_db(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    data = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=GITHUB_OAUTH_LINK_ENDPOINT,
        expected_schema=AuthGithubLinkEndpointSchemaConfig.primary_output_schema,
        expected_response_status=HTTPStatus.BAD_REQUEST,
        json={
            "user_email": get_test_name(),  # Create email guaranteed to not exist in database
            "gh_access_token": uuid.uuid4().hex,  # This logic should not be called until we validate the user is present
        },
    )

    assert data["message"] == "Email provided not associated with any user."
