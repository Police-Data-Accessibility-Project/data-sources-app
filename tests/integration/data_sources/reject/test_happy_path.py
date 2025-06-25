from db.enums import ApprovalStatus
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_data_sources_reject_happy_path(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    data_source = tdc.data_source()

    header = tdc.get_admin_tus().jwt_authorization_header

    def check_data_source_status(approval_status: ApprovalStatus):
        json_data = tdc.request_validator.get_data_source_by_id(
            headers=header, id=data_source.id
        )

        assert json_data["data"]["approval_status"] == approval_status.value

    check_data_source_status(ApprovalStatus.APPROVED)

    tdc.request_validator.reject_data_source(
        headers=header,
        data_source_id=data_source.id,
        rejection_note="This data source is not appropriate for our system",
        expected_json_content={
            "message": "Successfully rejected data source.",
        },
    )

    check_data_source_status(ApprovalStatus.REJECTED)
