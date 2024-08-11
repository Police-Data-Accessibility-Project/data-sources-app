from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup,
)
from tests.fixtures import flask_client_with_db, bypass_api_token_required, dev_db_connection


def test_search_get(flask_client_with_db, bypass_api_token_required):
    tus = create_test_user_setup(flask_client_with_db)

    response = flask_client_with_db.get(
        "/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions",
        headers=tus.authorization_header,
    )
    check_response_status(response, 200)
    data = response.json

    assert data["count"] > 0
    assert list(data["data"][0].keys()) == [
        "agency_name",
        "agency_supplied",
        "coverage_end",
        "coverage_start",
        "data_source_name",
        "description",
        "format",
        "id",
        "municipality",
        "record_type",
        "state",
        "url",
    ]
