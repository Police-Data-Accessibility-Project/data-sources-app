from unittest.mock import MagicMock

import pytest

from tests.middleware.request_content_population.populate_with_request_content.dto.constants import ROUTE_TO_PATCH
from tests.middleware.request_content_population.data import SAMPLE_REQUEST_ARGS


@pytest.fixture
def patched_get_data_from_source(monkeypatch):
    mock = MagicMock(
        return_value=SAMPLE_REQUEST_ARGS
    )
    monkeypatch.setattr(f"{ROUTE_TO_PATCH}.get_data_from_source", mock)
    return mock
