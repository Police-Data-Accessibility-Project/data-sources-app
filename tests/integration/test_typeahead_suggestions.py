from http import HTTPStatus

from middleware.primary_resource_logic.typeahead_suggestion_logic import (
    TypeaheadLocationsOuterResponseSchema,
    TypeaheadAgenciesOuterResponseSchema,
)
from tests.helper_scripts.helper_functions import (
    setup_get_typeahead_suggestion_test_data,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.conftest import flask_client_with_db


def test_typeahead_locations(flask_client_with_db):
    """
    Test that GET call to /typeahead/locations endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data()
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/typeahead/locations?query=xyl",
        expected_json_content={
            "suggestions": [
                {
                    "display_name": "Xylodammerung",
                    "locality": "Xylodammerung",
                    "county": "Arxylodon",
                    "state": "Xylonsylvania",
                    "type": "Locality",
                },
                {
                    "display_name": "Xylonsylvania",
                    "locality": None,
                    "county": None,
                    "state": "Xylonsylvania",
                    "type": "State",
                },
                {
                    "display_name": "Arxylodon",
                    "locality": None,
                    "county": "Arxylodon",
                    "state": "Xylonsylvania",
                    "type": "County",
                },
            ]
        },
        expected_schema=TypeaheadLocationsOuterResponseSchema,
    )


def test_typeahead_agencies(flask_client_with_db):
    """
    Test that GET call to /typeahead/agencies endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data()
    json_content = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/typeahead/agencies?query=xyl",
        expected_json_content={
            "suggestions": [
                {
                    "display_name": "Xylodammerung Police Agency",
                    "locality": "Xylodammerung",
                    "county": "Arxylodon",
                    "state": "XY",
                    "jurisdiction_type": "state",
                }
            ]
        },
        expected_schema=TypeaheadAgenciesOuterResponseSchema,
    )
