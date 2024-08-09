from typing import Optional

import pytest

from database_client.database_client import DatabaseClient
from tests.fixtures import client_with_mock_db, bypass_api_token_required
from tests.helper_scripts.common_test_data import TEST_RESPONSE
from tests.helper_scripts.helper_functions import (
    check_is_test_response,
)
from utilities.enums import RecordCategories


def mock_search_wrapper_all_parameters(
    db_client: DatabaseClient,
    state: str,
    record_categories: Optional[list[RecordCategories]] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_categories == [RecordCategories.POLICE]
    assert county == "Allegheny"
    assert locality == "Pittsburgh"

    return TEST_RESPONSE

def mock_search_wrapper_multiple_parameters(
    db_client: DatabaseClient,
    state: str,
    record_categories: Optional[list[RecordCategories]] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_categories == [RecordCategories.POLICE, RecordCategories.RESOURCE]
    assert county is None
    assert locality is None

    return TEST_RESPONSE

def mock_search_wrapper_minimal_parameters(
    db_client: DatabaseClient,
    state: str,
    record_categories: Optional[list[RecordCategories]] = None,
    county: Optional[str] = None,
    locality: Optional[str] = None,
):
    assert state == "Pennsylvania"
    assert record_categories is None
    assert county is None
    assert locality is None

    return TEST_RESPONSE


@pytest.mark.parametrize(
    "url, mock_search_wrapper_function",
    (
        (
            "/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions",
            mock_search_wrapper_all_parameters
        ),
        (
            "/search/search-location-and-record-type?state=Pennsylvania",
            mock_search_wrapper_minimal_parameters
        ),
        (
            "/search/search-location-and-record-type?state=Pennsylvania&record_category=Police+%26+Public+interactions%2CAgency-published+resources",
            mock_search_wrapper_multiple_parameters
        )
    )
)
def test_search_get_parameters(
        url,
        mock_search_wrapper_function,
        client_with_mock_db,
        monkeypatch,
        bypass_api_token_required,
):

    monkeypatch.setattr(
        "resources.Search.search_wrapper", mock_search_wrapper_function
    )

    response = client_with_mock_db.client.get(url)
    check_is_test_response(response)