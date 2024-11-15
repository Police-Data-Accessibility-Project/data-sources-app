from middleware.schema_and_dto_logic.primary_resource_schemas.typeahead_suggestion_schemas import (
    TypeaheadAgenciesOuterResponseSchema,
    TypeaheadLocationsOuterResponseSchema,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import TestDataCreatorFlask
from tests.helper_scripts.helper_functions import (
    setup_get_typeahead_suggestion_test_data,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.conftest import flask_client_with_db
from conftest import test_data_creator_flask, monkeysession


def test_typeahead_locations(flask_client_with_db):
    """
    Test that GET call to /typeahead/locations endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data()
    expected_suggestions = [
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
    suggestions = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/typeahead/locations?query=xyl",
        expected_schema=TypeaheadLocationsOuterResponseSchema,
    )["suggestions"]
    for suggestion in suggestions:
        # Don't check for matching location id
        del suggestion["location_id"]

    assert suggestions == expected_suggestions


def test_typeahead_agencies(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /typeahead/agencies endpoint successfully retrieves data
    """
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    location_id = tdc.locality(locality_name="Qzy")
    agency_id = tdc.agency(agency_name="Qzy").id
    tdc.refresh_typeahead_agencies()

    json_content = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/typeahead/agencies?query=qzy",
        expected_schema=TypeaheadAgenciesOuterResponseSchema,
    )
    assert len(json_content["suggestions"]) > 0
    result = json_content["suggestions"][0]

    assert "Qzy" in result["display_name"]
    assert result["id"] == int(agency_id)
