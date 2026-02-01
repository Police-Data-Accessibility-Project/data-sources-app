from http import HTTPStatus

from middleware.enums import RecordTypesEnum
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_post_data_source_with_url_fragment(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that posting a data source with a URL containing a fragment (#)
    returns a 400 Bad Request with a helpful error message.
    """
    response = test_data_creator_flask.request_validator.post(
        endpoint="/data-sources",
        headers=test_data_creator_flask.standard_user().jwt_authorization_header,
        json={
            "entry_data": {
                "source_url": "https://www.example.com/page#fragment",
                "name": "Test Data Source with Fragment",
                "description": "This should fail due to URL fragment",
                "record_type_name": RecordTypesEnum.CRIME_STATISTICS.value,
            },
            "linked_agency_ids": [],
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )

    # Verify the error message is helpful
    assert "fragment" in response["message"].lower()
    assert "#" in response["message"]


def test_post_data_source_duplicate_url(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that posting a duplicate data source (same URL and record type)
    returns a 409 Conflict with a helpful error message.
    """
    # First, create a data source successfully
    test_url = "https://www.example.com/unique-test-url"
    record_type = RecordTypesEnum.CRIME_STATISTICS

    test_data_creator_flask.request_validator.post(
        endpoint="/data-sources",
        headers=test_data_creator_flask.standard_user().jwt_authorization_header,
        json={
            "entry_data": {
                "source_url": test_url,
                "name": "Original Data Source",
                "description": "Original data source",
                "record_type_name": record_type.value,
            },
            "linked_agency_ids": [],
        },
        expected_response_status=HTTPStatus.OK,
    )

    # Now try to create a duplicate with the same URL and record type
    response = test_data_creator_flask.request_validator.post(
        endpoint="/data-sources",
        headers=test_data_creator_flask.standard_user().jwt_authorization_header,
        json={
            "entry_data": {
                "source_url": test_url,
                "name": "Duplicate Data Source",
                "description": "This should fail due to duplicate URL and record type",
                "record_type_name": record_type.value,
            },
            "linked_agency_ids": [],
        },
        expected_response_status=HTTPStatus.CONFLICT,
    )

    # Verify the error message is helpful
    assert "duplicate" in response["message"].lower()
    assert "url" in response["message"].lower()
