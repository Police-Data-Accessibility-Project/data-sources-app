from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import client_with_mock_db
from unittest.mock import patch, MagicMock
from tests.helper_functions import check_response_status

import json
from http import HTTPStatus


def test_login_with_github_post(client_with_mock_db, monkeypatch):
    mock_setup_callback_session = MagicMock()
    monkeypatch.setattr("resources.LoginWithGithub.setup_callback_session", mock_setup_callback_session)
    mock_redirect_to_github_authorization = MagicMock(return_value=({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT))
    monkeypatch.setattr("resources.LoginWithGithub.redirect_to_github_authorization", mock_redirect_to_github_authorization)

    response = client_with_mock_db.client.post("auth/login-with-github")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LOGIN_WITH_GITHUB
    )
    mock_redirect_to_github_authorization.assert_called_once()
