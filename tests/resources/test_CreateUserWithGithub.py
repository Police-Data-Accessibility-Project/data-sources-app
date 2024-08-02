from unittest.mock import MagicMock
from tests.fixtures import client_with_mock_db

from middleware.enums import CallbackFunctionsEnum
from tests.helper_functions import check_response_status, DynamicMagicMock
from tests.helper_scripts.common_test_data import TEST_RESPONSE


class TestCreateUserWithGithubMocks(DynamicMagicMock):
    setup_callback_session: MagicMock
    redirect_to_github_authorization: MagicMock

PATCH_PREFIX = "resources.CreateUserWithGithub."

def test_create_user_with_github_post(
    client_with_mock_db,
    monkeypatch,
):
    mock = TestCreateUserWithGithubMocks(
        patch_paths={
            "setup_callback_session": f"{PATCH_PREFIX}setup_callback_session",
            "redirect_to_github_authorization": f"{PATCH_PREFIX}redirect_to_github_authorization",
        },
        return_values={"redirect_to_github_authorization": TEST_RESPONSE},
    )

    response = client_with_mock_db.client.post("auth/create-user-with-github")
    check_response_status(response, TEST_RESPONSE.status_code)
    mock.setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB
    )
    mock.redirect_to_github_authorization.assert_called_once()
