from http import HTTPStatus

from db.enums import ApprovalStatus
from db.models.implementations.core.agency.core import Agency
from db.models.implementations.link import LinkAgencyLocation
from middleware.enums import JurisdictionType, AgencyType
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_proposal_agency_create(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    location_id = tdc.locality()

    tdc.request_validator.create_proposal_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        data={
            "agency_info": {
                "name": "Test Agency",
                "jurisdiction_type": JurisdictionType.LOCAL.value,
                "agency_type": AgencyType.COURT.value,
                "homepage_url": "https://example.com",
            },
            "location_ids": [location_id],
        },
    )

    # Confirm agency in database
    agencies = tdc.db_client.get_all(Agency)
    assert len(agencies) == 1
    assert agencies[0]["name"] == "Test Agency"
    assert agencies[0]["jurisdiction_type"] == JurisdictionType.LOCAL.value
    assert agencies[0]["agency_type"] == AgencyType.COURT.value
    assert agencies[0]["homepage_url"] == "https://example.com"
    assert agencies[0]["creator_user_id"] == tdc.get_admin_tus().user_info.user_id
    assert agencies[0]["approval_status"] == ApprovalStatus.PENDING.value

    # Confirm agency location link in database
    links = tdc.db_client.get_all(LinkAgencyLocation)
    assert len(links) == 1
    assert links[0]["agency_id"] == agencies[0]["id"]
    assert links[0]["location_id"] == location_id


def test_proposal_agency_create_fail_on_approval_status_included(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    location_id = tdc.locality()

    tdc.request_validator.create_proposal_agency(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        data={
            "agency_info": {
                "name": "Test Agency",
                "jurisdiction_type": JurisdictionType.LOCAL.value,
                "agency_type": AgencyType.COURT.value,
                "homepage_url": "https://example.com",
                "approval_status": ApprovalStatus.APPROVED.value,
            },
            "location_ids": [location_id],
        },
        expected_json_content={
            "message": "{'agency_info': {'approval_status': ['Unknown field.']}}"
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
    )
