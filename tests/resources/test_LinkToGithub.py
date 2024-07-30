from middleware.enums import CallbackFunctionsEnum
from tests.fixtures import client_with_mock_db
from unittest.mock import patch, MagicMock
from tests.helper_functions import check_response_status

import json
from http import HTTPStatus

def test_link_to_github_post(client_with_mock_db, monkeypatch):
    mock_parse_args_values = {
        "redirect_to": MagicMock(),
        "user_email": MagicMock()
    }
    mock_parse_args = MagicMock(return_value=mock_parse_args_values)
    monkeypatch.setattr("resources.LinkToGithub.link_to_github_parser.parse_args", mock_parse_args)
    mock_setup_callback_session = MagicMock()
    monkeypatch.setattr("resources.LinkToGithub.setup_callback_session", mock_setup_callback_session)
    mock_redirect_to_github_authorization = MagicMock(return_value = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT))
    monkeypatch.setattr("resources.LinkToGithub.redirect_to_github_authorization", mock_redirect_to_github_authorization)
    response = client_with_mock_db.client.post("auth/link-to-github")
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    mock_redirect_to_github_authorization.assert_called_once()
    mock_setup_callback_session.assert_called_once_with(
        callback_functions_enum=CallbackFunctionsEnum.LINK_TO_GITHUB,
        redirect_to=mock_parse_args_values["redirect_to"],
        user_email=mock_parse_args_values["user_email"],
    )