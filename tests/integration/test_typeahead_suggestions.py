from http import HTTPStatus

from tests.helper_scripts.helper_functions import (
    check_response_status,
    setup_get_typeahead_suggestion_test_data,
)
from tests.fixtures import client_with_db, dev_db_connection


def test_typeahead_suggestions(client_with_db, dev_db_connection):
    """
    Test that GET call to /typeahead-suggestions endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data(dev_db_connection.cursor())
    dev_db_connection.commit()
    response = client_with_db.get("/search/typeahead-suggestions?query=xyl")
    check_response_status(response, HTTPStatus.OK.value)
    results = response.json["suggestions"]
    assert results[0]["display_name"] == "Xylodammerung"
    assert results[0]["locality"] == "Xylodammerung"
    assert results[0]["county"] == "Arxylodon"
    assert results[0]["state"] == "Xylonsylvania"
    assert results[0]["type"] == "Locality"

    assert results[1]["display_name"] == "Xylonsylvania"
    assert results[1]["locality"] is None
    assert results[1]["county"] is None
    assert results[1]["state"] == "Xylonsylvania"
    assert results[1]["type"] == "State"

    assert results[2]["display_name"] == "Arxylodon"
    assert results[2]["locality"] is None
    assert results[2]["county"] == "Arxylodon"
    assert results[2]["state"] == "Xylonsylvania"
    assert results[2]["type"] == "County"
