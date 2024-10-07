from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tests.conftest import (
    ClientWithMockDB,
    client_with_mock_db,
    mock_database_client,
    bypass_authentication_required,
)


@dataclass
class ResourceTestSetup:
    client_with_mock_db: ClientWithMockDB = None
    mock: MagicMock = None
    monkeypatch: MonkeyPatch = None


@pytest.fixture
def resource_test_setup(
    client_with_mock_db,
    mock_database_client,
    bypass_authentication_required,
    monkeypatch,
) -> ResourceTestSetup:
    mock = MagicMock()
    mock.db_client = mock_database_client
    mock.access_info = bypass_authentication_required
    return ResourceTestSetup(
        client_with_mock_db=client_with_mock_db,
        mock=mock,
        monkeypatch=monkeypatch,
    )
