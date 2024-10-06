from tests.helper_scripts.helper_functions import (
    create_test_user_setup,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.conftest import (
    dev_db_connection,
    flask_client_with_db,
    bypass_api_key_required,
)


def test_search_get(flask_client_with_db, bypass_api_key_required):
    tus = create_test_user_setup(flask_client_with_db)

    data = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/search/search-location-and-record-type?state=Pennsylvania&county=Allegheny&locality=Pittsburgh&record_categories=Police%20%26%20Public%20Interactions",
        headers=tus.api_authorization_header,
    )

    jurisdictions = ["federal", "state", "county", "locality"]

    assert list(data.keys()) == ["count", "data"]
    assert list(data["data"].keys()).sort() == jurisdictions.sort()
    assert data["count"] > 0

    jurisdiction_count = 0
    for jurisdiction in jurisdictions:
        assert list(data["data"][jurisdiction].keys()) == ["count", "results"]
        jurisdiction_count += data["data"][jurisdiction]["count"]
        if data["data"][jurisdiction]["count"] > 0:
            assert (
                list(data["data"][jurisdiction]["results"][0].keys()).sort()
                == [
                    "agency_name",
                    "agency_supplied",
                    "coverage_end",
                    "coverage_start",
                    "data_source_name",
                    "description",
                    "jurisdiction_type",
                    "record_format",
                    "id",
                    "municipality",
                    "record_type",
                    "state",
                    "url",
                ].sort()
            )

    assert jurisdiction_count == data["count"]
