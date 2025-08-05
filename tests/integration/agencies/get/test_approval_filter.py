from db.enums import ApprovalStatus
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_agencies_get_approval_filter(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies endpoint properly retrieves a nonzero amount of data
    """
    # Delete all agencies
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    # Create two agencies with approved status
    tdc.agency()
    tdc.agency()

    # Create one agency with pending status
    tdc.agency(approval_status=ApprovalStatus.PENDING)

    # Get all agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Check that all agencies are retrieved
    assert len(response_json["data"]) == 3

    # Get all approved agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        approval_status=ApprovalStatus.APPROVED,
    )

    # Check that only two agencies are retrieved
    assert len(response_json["data"]) == 2

    # Get all pending agencies
    response_json = tdc.request_validator.get_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        approval_status=ApprovalStatus.PENDING,
    )

    # Check that only one agency is retrieved
    assert len(response_json["data"]) == 1
