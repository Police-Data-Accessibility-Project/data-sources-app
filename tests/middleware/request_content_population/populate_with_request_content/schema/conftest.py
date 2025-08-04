from unittest.mock import MagicMock

import pytest

from tests.middleware.request_content_population.populate_with_request_content.schema.constants import (
    PATCH_ROOT,
)


@pytest.fixture
def patched_get_source_data_info_from_sources(monkeypatch):
    mock = MagicMock(
        return_value={
            "example_dto_with_enum": {"example_enum": "a"},
            "example_dto": {
                "example_string": "my example string",
                "example_query_string": "my example query string",
            },
        }
    )
    monkeypatch.setattr(f"{PATCH_ROOT}._get_data_from_sources", mock)
    return mock
