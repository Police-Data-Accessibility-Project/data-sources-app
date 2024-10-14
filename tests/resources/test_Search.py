import pytest

from database_client.database_client import DatabaseClient
from middleware.schema_and_dto_logic.primary_resource_schemas.search_schemas import SearchRequests
from tests.conftest import client_with_mock_db, bypass_api_key_required
from tests.helper_scripts.constants import TEST_RESPONSE
from tests.helper_scripts.helper_functions import (
    check_is_test_response,
)
from utilities.enums import RecordCategories


def mock_search_wrapper_all_parameters(
    db_client: DatabaseClient,
    dto: SearchRequests,
):
    assert dto.state == "Pennsylvania"
    assert dto.record_categories == [RecordCategories.POLICE]
    assert dto.county == "Allegheny"
    assert dto.locality == "Pittsburgh"

    return TEST_RESPONSE


def mock_search_wrapper_multiple_parameters(
    db_client: DatabaseClient,
    dto: SearchRequests,
):
    assert dto.state == "Pennsylvania"
    assert dto.record_categories == [RecordCategories.POLICE, RecordCategories.RESOURCE]
    assert dto.county is None
    assert dto.locality is None

    return TEST_RESPONSE


def mock_search_wrapper_minimal_parameters(
    db_client: DatabaseClient,
    dto: SearchRequests,
):
    assert dto.state == "Pennsylvania"
    assert dto.record_categories is None
    assert dto.county is None
    assert dto.locality is None

    return TEST_RESPONSE


@pytest.mark.parametrize(
    "url, mock_search_wrapper_function",
    (
        (
            "/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_categories=Police%20%26%20Public%20Interactions",
            mock_search_wrapper_all_parameters,
        ),
        (
            "/search/search-location-and-record-type?state=Pennsylvania",
            mock_search_wrapper_minimal_parameters,
        ),
        (
            "/search/search-location-and-record-type?state=Pennsylvania&record_categories=Police+%26+Public+interactions%2CAgency-published+resources",
            mock_search_wrapper_multiple_parameters,
        ),
    ),
)
def test_search_get_parameters(
    url,
    mock_search_wrapper_function,
    client_with_mock_db,
    monkeypatch,
    bypass_api_key_required,
):

    monkeypatch.setattr("resources.Search.search_wrapper", mock_search_wrapper_function)

    response = client_with_mock_db.client.get(url)
    check_is_test_response(response)
