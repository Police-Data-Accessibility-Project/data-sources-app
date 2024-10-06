from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.primary_resource_logic.archives_queries import (
    update_archives_data,
)


@pytest.fixture
def make_response_mock(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr(
        "middleware.primary_resource_logic.archives_queries.make_response", mock
    )
    return mock


def test_update_archives_data_broken_as_of(make_response_mock):
    mock = MagicMock()

    # Call function
    update_archives_data(
        mock.db_client, mock.data_id, mock.last_cached, mock.broken_as_of
    )

    mock.db_client.update_url_status_to_broken.assert_called_with(
        mock.data_id, mock.broken_as_of
    )
    mock.db_client.update_last_cached.assert_called_with(mock.data_id, mock.last_cached)
    make_response_mock.assert_called_with({"status": "success"}, HTTPStatus.OK)


def test_update_archives_data_not_broken_as_of(make_response_mock):
    mock = MagicMock()

    # Call function
    update_archives_data(mock.db_client, mock.data_id, mock.last_cached, None)

    mock.db_client.update_url_status_to_broken.assert_not_called()
    mock.db_client.update_last_cached.assert_called_with(mock.data_id, mock.last_cached)

    make_response_mock.assert_called_with({"status": "success"}, HTTPStatus.OK)
