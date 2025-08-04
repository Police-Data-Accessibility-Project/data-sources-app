from db.enums import ApprovalStatus
from middleware.enums import JurisdictionType, AgencyType, RecordTypes
from middleware.schema_and_dto.schemas.agencies.info.post import AgencyInfoPostSchema
from tests.helpers.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from utilities.enums import RecordCategoryEnum


def test_search_federal(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    # Create two approved federal agencies
    agency_ids = []
    for i in range(2):
        a_id = tdc.request_validator.create_agency(
            headers=tdc.get_admin_tus().jwt_authorization_header,
            agency_post_parameters={
                "agency_info": generate_test_data_from_schema(
                    schema=AgencyInfoPostSchema(),
                    override={
                        "jurisdiction_type": JurisdictionType.FEDERAL.value,
                        "approval_status": ApprovalStatus.APPROVED.value,
                        "agency_type": AgencyType.POLICE.value,
                    },
                ),
            },
        )
        agency_ids.append(a_id)

    # Link 2 approved data sources to each federal agency
    record_types = list(RecordTypes)
    for i in range(2):
        for j in range(2):
            d_id = tdc.tdcdb.data_source(
                approval_status=ApprovalStatus.APPROVED, record_type=record_types[j]
            ).id
            tdc.link_data_source_to_agency(
                data_source_id=d_id,
                agency_id=agency_ids[i],
            )

    # Run search and confirm 4 results
    results = tdc.request_validator.federal_search(
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    assert len(results["results"]) == 4

    # Check results are the same as if we did a search on all record categories
    results_implicit = tdc.request_validator.federal_search(
        headers=tdc.get_admin_tus().jwt_authorization_header,
        record_categories=[
            rc for rc in RecordCategoryEnum if rc != RecordCategoryEnum.ALL
        ],
    )

    assert len(results_implicit["results"]) == 4

    # Search on page 2 and confirm no results
    results = tdc.request_validator.federal_search(
        headers=tdc.get_admin_tus().jwt_authorization_header, page=2
    )

    assert len(results["results"]) == 0
