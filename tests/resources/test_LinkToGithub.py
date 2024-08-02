from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import client_with_mock_db, bypass_api_required
from unittest.mock import MagicMock
from tests.helper_functions import check_response_status, DynamicMagicMock

from tests.helper_scripts.common_test_data import TEST_RESPONSE


class TestLinkToGithubMocks(DynamicMagicMock):
    parse_args: MagicMock
    setup_callback_session: MagicMock
    redirect_to_github_authorization: MagicMock


PATCH_PREFIX = "resources.LinkToGithub."

PATCH_PATHS = {
    "parse_args": f"{PATCH_PREFIX}link_to_github_parser.parse_args",
    "setup_callback_session": f"{PATCH_PREFIX}setup_callback_session",
    "redirect_to_github_authorization": f"{PATCH_PREFIX}redirect_to_github_authorization",
}



def test_link_to_github_post(client_with_mock_db, bypass_api_required):
    mock_parse_args_values = {"redirect_to": MagicMock(), "user_email": MagicMock()}
    mock = TestLinkToGithubMocks(
        patch_paths=PATCH_PATHS,
        return_values={
            "parse_args": mock_parse_args_values,
            "redirect_to_github_authorization": TEST_RESPONSE
        }
    )

    response = client_with_mock_db.client.post("auth/link-to-github")

    check_response_status(response, TEST_RESPONSE.status_code)
    mock.redirect_to_github_authorization.assert_called_once()
    mock.setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        redirect_to=mock_parse_args_values["redirect_to"],
        user_email=mock_parse_args_values["user_email"],
    )
