from tests.helper_scripts.common_test_data import (
    get_test_name,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.common_asserts import (
    assert_jwt_token_matches_user_email,
)
from tests.integration.oauth.helpers import login_with_github, setup_github_mocks


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
