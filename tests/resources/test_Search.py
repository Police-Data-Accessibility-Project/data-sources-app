from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock

from database_client.database_client import DatabaseClient
from tests.fixtures import client_with_mock_db, bypass_api_required
from tests.helper_functions import check_response_status
from utilities.enums import RecordCategories


def mock_search_wrapper(
    db_client: DatabaseClient,
    state: str,
    record_category: Optional[RecordCategories] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_category == RecordCategories.POLICE
    assert county == "Allegheny"
    assert locality == "Pittsburgh"

    mock_response = ({"message": "Test Response"}, HTTPStatus.IM_A_TEAPOT)
    return mock_response


def test_search_get(client_with_mock_db, monkeypatch, bypass_api_required):

    monkeypatch.setattr("resources.Search.search_wrapper", mock_search_wrapper)

    response = client_with_mock_db.client.get(
        "/search?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions"
    )
    check_response_status(response, HTTPStatus.IM_A_TEAPOT)
    assert response.json == {"message": "Test Response"}
