from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from tests.fixtures import client_with_mock_db


def mock_get_agencies(cursor, page: int):
    return ({"message": f"Test Response for page {page}"}, HTTPStatus.IM_A_TEAPOT)


def test_get_agencies(client_with_mock_db, monkeypatch):

    monkeypatch.setattr("middleware.security.validate_token", lambda: None)
    monkeypatch.setattr("resources.Agencies.get_agencies", mock_get_agencies)

    response = client_with_mock_db.client.get(
        "/agencies/3",
        headers={"Authorization": "Bearer test_token"},
    )
    assert response.status_code == HTTPStatus.IM_A_TEAPOT
    assert response.json == {"message": "Test Response for page 3"}
