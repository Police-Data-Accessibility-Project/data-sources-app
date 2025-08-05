from db.enums import SortOrder
from middleware.enums import JurisdictionType
from tests.helpers.asserts import assert_expected_get_many_result
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_agencies_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    tdc = test_data_creator_flask
    tdc.agency()
    tdc.agency()
    tdc.agency(jurisdiction_type=JurisdictionType.FEDERAL)
    tus = tdc.standard_user()

    # Check basic data retrieval
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    data_asc = response_json["data"]

    # Test pagination functionality
    response_json_2 = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
        page=2,
    )

    assert response_json != response_json_2

    # Test sort functionality
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.DESCENDING,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    data_desc = response_json["data"]

    assert data_asc != data_desc
    assert data_asc[0]["name"] < data_desc[0]["name"]

    assert data_asc[0]["name"] == data_asc[0]["submitted_name"]

    # Test limit functionality
    response_json = tdc.request_validator.get_agency(
        headers=tus.api_authorization_header,
        sort_by="name",
        sort_order=SortOrder.ASCENDING,
        limit=1,
    )

    assert_expected_get_many_result(
        response_json=response_json,
        expected_non_null_columns=["id"],
    )
    assert len(response_json["data"]) == 1
