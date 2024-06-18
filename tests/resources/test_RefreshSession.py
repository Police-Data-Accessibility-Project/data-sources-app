from unittest.mock import MagicMock

import pytest
from http import HTTPStatus

from middleware.custom_exceptions import TokenNotFoundError
from middleware.login_queries import SessionTokenUserData
from tests.fixtures import client_with_mock_db
from tests.helper_functions import check_response_status


@pytest.fixture
def mock_cursor(client_with_mock_db):
    return client_with_mock_db.mock_db.cursor.return_value


@pytest.fixture
def mock_get_session_token_user_data(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("resources.RefreshSession.get_session_token_user_data", mock)
    return mock


@pytest.fixture
def mock_delete_session_token(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("resources.RefreshSession.delete_session_token", mock)
    return mock


@pytest.fixture
def mock_create_session_token(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("resources.RefreshSession.create_session_token", mock)
    return mock


def test_post_refresh_session_happy_path(
    client_with_mock_db,
    mock_cursor,
    mock_get_session_token_user_data,
    mock_delete_session_token,
    mock_create_session_token,
):
    test_session_token_user_data = SessionTokenUserData(
        id="test_id", email="test_email"
    )
    mock_get_session_token_user_data.return_value = test_session_token_user_data
    mock_create_session_token.return_value = "new_test_session_token"

    response = client_with_mock_db.client.post(
        "/refresh-session",
        json={
            "session_token": "old_test_session_token",
        },
    )
    check_response_status(response, HTTPStatus.OK.value)
    assert response.json == {
        "message": "Successfully refreshed session token",
        "data": "new_test_session_token",
    }
    mock_get_session_token_user_data.assert_called_once_with(
        mock_cursor, "old_test_session_token"
    )
    mock_delete_session_token.assert_called_once_with(
        mock_cursor, "old_test_session_token"
    )
    mock_create_session_token.assert_called_once_with(
        mock_cursor, test_session_token_user_data.id, test_session_token_user_data.email
    )
    client_with_mock_db.mock_db.commit.assert_called_once()


def test_post_refresh_session_token_not_found(
    client_with_mock_db,
    mock_cursor,
    mock_get_session_token_user_data,
    mock_delete_session_token,
    mock_create_session_token,
):
    """
    Test that RefreshSessionPost behaves as expected when the session token is not found
    :param client_with_mock_db:
    :return:
    """
    mock_get_session_token_user_data.side_effect = TokenNotFoundError
    response = client_with_mock_db.client.post(
        "/refresh-session",
        json={
            "session_token": "old_test_session_token",
        },
    )

    check_response_status(response, HTTPStatus.FORBIDDEN.value)
    assert response.json == {
        "message": "Invalid session token",
    }
    mock_get_session_token_user_data.assert_called_once_with(
        mock_cursor, "old_test_session_token"
    )
    mock_delete_session_token.assert_not_called()
    mock_create_session_token.assert_not_called()
    client_with_mock_db.mock_db.commit.assert_not_called()


def test_post_refresh_session_unexpected_error(
    client_with_mock_db,
    mock_cursor,
    mock_get_session_token_user_data,
    mock_delete_session_token,
    mock_create_session_token,
):
    """
    Test that RefreshSessionPost behaves as expected when there is an unexpected error
    :param client_with_mock_db:
    :return:
    """
    mock_get_session_token_user_data.side_effect = Exception(
        "An unexpected error occurred"
    )
    response = client_with_mock_db.client.post(
        "/refresh-session",
        json={
            "session_token": "old_test_session_token",
        },
    )

    check_response_status(response, HTTPStatus.INTERNAL_SERVER_ERROR.value)
    assert response.json["message"] == "An unexpected error occurred"
    mock_get_session_token_user_data.assert_called_once_with(
        mock_cursor, "old_test_session_token"
    )
    mock_delete_session_token.assert_not_called()
    mock_create_session_token.assert_not_called()
    client_with_mock_db.mock_db.commit.assert_not_called()
