"""
Tests resources which result in a redirection to the `/callback` endpoint
"""

from unittest.mock import MagicMock

import pytest

from middleware.enums import CallbackFunctionsEnum
from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock
from tests.helper_scripts.constants import TEST_RESPONSE
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.conftest import client_with_mock_db, bypass_api_key_required


class TestPreCallbackResources(DynamicMagicMock):
    setup_callback_session: MagicMock
    redirect_to_github_authorization: MagicMock


@pytest.mark.parametrize(
    "resource_module_name, endpoint, json_data, setup_callback_session_expected_args",
    (
        (
            "LoginWithGithub",
            "auth/login-with-github",
            {},
            {"callback_functions_enum": CallbackFunctionsEnum.LOGIN_WITH_GITHUB},
        ),
        (
            "CreateUserWithGithub",
            "auth/create-user-with-github",
            {},
            {"callback_functions_enum": CallbackFunctionsEnum.CREATE_USER_WITH_GITHUB},
        ),
        (
            "LinkToGithub",
            "auth/link-to-github",
            {"redirect_to": "test_redirect_to", "user_email": "test_user_email"},
            {
                "callback_functions_enum": CallbackFunctionsEnum.LINK_TO_GITHUB,
                "redirect_to": "test_redirect_to",
                "user_email": "test_user_email",
            },
        ),
    ),
)
def test_pre_callback_resources(
    resource_module_name,
    endpoint,
    json_data,
    setup_callback_session_expected_args,
    client_with_mock_db,
    bypass_api_key_required,
):
    mock = TestPreCallbackResources(
        patch_root=f"resources.{resource_module_name}",
        return_values={"redirect_to_github_authorization": TEST_RESPONSE},
    )

    response = client_with_mock_db.client.post(endpoint, json=json_data)
    check_response_status(response, TEST_RESPONSE.status_code)
    mock.setup_callback_session.assert_called_once_with(
        **setup_callback_session_expected_args
    )
    mock.redirect_to_github_authorization.assert_called_once()
