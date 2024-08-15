from tests.helper_scripts.helper_functions import (
    check_response_status,
    create_test_user_setup,
    run_and_validate_request,
)
from tests.fixtures import (
    flask_client_with_db,
    bypass_api_key_required,
    dev_db_connection,
)


def test_search_get(flask_client_with_db, bypass_api_key_required):
    tus = create_test_user_setup(flask_client_with_db)

    data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_category=Police%20%26%20Public%20Interactions",
        headers=tus.api_authorization_header,
    )

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
