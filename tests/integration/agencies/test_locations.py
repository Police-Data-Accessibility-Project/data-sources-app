from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_agencies_locations(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    # Create agency
    agency_id = tdc.agency().id

    location_id = tdc.locality()

    # Add location
    tdc.request_validator.add_location_to_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        agency_id=agency_id,
        location_id=location_id,
    )

    # Get agency and confirm presence
    result = tdc.request_validator.get_agency_by_id(
        headers=tdc.get_admin_tus().api_authorization_header,
        id=agency_id,
    )

    assert len(result["data"]["locations"]) == 2

    # Remove location
    tdc.request_validator.remove_location_from_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        agency_id=agency_id,
        location_id=location_id,
    )

    # Get agency and confirm absence
    result = tdc.request_validator.get_agency_by_id(
        headers=tdc.get_admin_tus().api_authorization_header,
        id=agency_id,
    )

    assert len(result["data"]["locations"]) == 1
