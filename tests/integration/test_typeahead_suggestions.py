from http import HTTPStatus

from tests.helper_scripts.helper_functions import (
    setup_get_typeahead_suggestion_test_data,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status
from tests.fixtures import flask_client_with_db, dev_db_connection


def test_typeahead_suggestions(flask_client_with_db, dev_db_connection):
    """
    Test that GET call to /typeahead-suggestions endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data(dev_db_connection.cursor())
    dev_db_connection.commit()
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
    )
