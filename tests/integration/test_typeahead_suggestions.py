from middleware.schema_and_dto.schemas.typeahead.locations import (
    TypeaheadLocationsOuterResponseSchema,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.helper_functions_complex import (
    setup_get_typeahead_suggestion_test_data,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_typeahead_locations(flask_client_with_db):
    """
    Test that GET call to /typeahead/locations endpoint successfully retrieves data
    """
    setup_get_typeahead_suggestion_test_data()
    expected_suggestions = [
        {
            "display_name": "Xylodammerung, Arxylodon, Xylonsylvania",
            "locality_name": "Xylodammerung",
            "county_name": "Arxylodon",
            "state_name": "Xylonsylvania",
            "type": "Locality",
        },
        {
            "display_name": "Xylonsylvania",
            "locality_name": None,
            "county_name": None,
            "state_name": "Xylonsylvania",
            "type": "State",
        },
        {
            "display_name": "Arxylodon, Xylonsylvania",
            "locality_name": None,
            "county_name": "Arxylodon",
            "state_name": "Xylonsylvania",
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

    # Even the most absurd misspellings should pull back something
    json_content = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint="/typeahead/locations?query=AbsolutelyGodawfulMisspelledEntryThatShouldMatchNothing",
        expected_schema=TypeaheadLocationsOuterResponseSchema,
    )
    assert len(json_content["suggestions"]) >= 1


def test_typeahead_locations_cleveland(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /typeahead/locations endpoint successfully retrieves the correct
    Cleveland in the notorious Cleveland Case,
    where there are 17 Clevelands in the database
    """
    tdc = test_data_creator_flask
    tdc.tdcdb.create_states()

    clevelands = [
        ["NC", "Rowan"],
        ["WI", "Manitowoc"],
        ["OK", "Pawnee"],
        ["MO", "Cass"],
        ["MN", "Le Sueur"],
        ["MI", "Jackson"],
        ["OR", "Multnomah"],
        ["IN", "Washington"],
        ["TX", "Liberty"],
        ["AL", "Blount"],
        ["OH", "Cuyahoga"],
        ["TN", "Bradley"],
        ["MS", "Bolivar"],
        ["GA", "White"],
    ]
    for state_name, county_name in clevelands:
        tdc.tdcdb.county(state_iso=state_name, county_name=county_name)
        tdc.locality(
            locality_name="Cleveland", county_name=county_name, state_iso=state_name
        )
    tdc.refresh_typeahead_locations()

    json_content = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/typeahead/locations?query=cleveland ohio",
        expected_schema=TypeaheadLocationsOuterResponseSchema,
    )

    assert len(json_content["suggestions"]) >= 1
    result = json_content["suggestions"][0]

    assert result["locality_name"] == "Cleveland"
    assert result["county_name"] == "Cuyahoga"
    assert result["state_name"] == "Ohio"


def test_typeahead_agencies_approved(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /typeahead/agencies endpoint successfully retrieves data
    """
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    tdc.locality(locality_name="Qzy")
    agency_id = tdc.agency(agency_name="Qzy").id
    tdc.refresh_typeahead_agencies()

    json_content = tdc.request_validator.typeahead_agency(
        query="qzy",
    )

    assert len(json_content["suggestions"]) > 0
    result = json_content["suggestions"][0]

    assert "Qzy" in result["display_name"]
    assert result["id"] == int(agency_id)

    # Even the most absurd misspellings should pull back something
    json_content = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint="/typeahead/locations?query=AbsolutelyGodawfulMisspelledEntryThatShouldMatchNothing",
        expected_schema=TypeaheadLocationsOuterResponseSchema,
    )
    assert len(json_content["suggestions"]) >= 1
