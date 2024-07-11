import datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from middleware.archives_queries import (
    update_archives_data,
)
from tests.helper_functions import (
    DynamicMagicMock,
)


class UpdateArchivesDataMocks(DynamicMagicMock):
    db_client: MagicMock
    data_id: MagicMock
    last_cached: MagicMock
    broken_as_of: MagicMock
    archives_put_broken_as_of_results: MagicMock
    archives_put_last_cached_results: MagicMock
    make_response: MagicMock


@pytest.fixture
def setup_update_archives_data_mocks(monkeypatch):
    mock = UpdateArchivesDataMocks()
    monkeypatch.setattr("middleware.archives_queries.make_response", mock.make_response)
    return mock


def test_update_archives_data_broken_as_of(setup_update_archives_data_mocks):
    mock = setup_update_archives_data_mocks

    # Call function
    update_archives_data(
        mock.db_client, mock.data_id, mock.last_cached, mock.broken_as_of
    )

    mock.db_client.update_url_status_to_broken.assert_called_with(
        mock.data_id, mock.broken_as_of, mock.last_cached
    )
    mock.archives_put_last_cached_results.assert_not_called()
    mock.make_response.assert_called_with({"status": "success"}, HTTPStatus.OK)


def test_update_archives_data_not_broken_as_of(setup_update_archives_data_mocks):
    mock = setup_update_archives_data_mocks

    # Call function
    update_archives_data(mock.db_client, mock.data_id, mock.last_cached, None)

    mock.db_client.update_url_status_to_broken.assert_not_called()
    mock.db_client.update_last_cached.assert_called_with(mock.data_id, mock.last_cached)

    mock.make_response.assert_called_with({"status": "success"}, HTTPStatus.OK)
