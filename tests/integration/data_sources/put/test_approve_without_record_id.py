from http import HTTPStatus

from db.enums import ApprovalStatus
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_data_sources_by_id_put_approve_without_record_id(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that the data source can't be approved without a record id
    """

    # Arrange
    tdc = test_data_creator_flask
    data_source_id = tdc.tdcdb.data_source(
        approval_status=ApprovalStatus.PENDING, record_type=None
    ).id

    tdc.request_validator.update_data_source(
        tus=tdc.get_admin_tus(),
        data_source_id=data_source_id,
        entry_data={"approval_status": ApprovalStatus.APPROVED.value},
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": "Record type is required for approval."},
    )
