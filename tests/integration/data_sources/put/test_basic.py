import uuid

from db.enums import (
    AgencyAggregation,
    DetailLevel,
    AccessType,
    UpdateMethod,
    RetentionSchedule,
    URLStatus,
)
from endpoints.schema_config.instantiations.data_sources.by_id.get import (
    DataSourcesByIDGetEndpointSchemaConfig,
)
from middleware.enums import RecordTypes
from tests.helper_scripts.common_asserts import assert_contains_key_value_pairs
from tests.helper_scripts.common_test_data import get_test_name
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_sources_by_id_put(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """
    tdc = test_data_creator_flask
    cdr = tdc.data_source()

    entry_data = {
        "name": get_test_name(),
        "description": uuid.uuid4().hex,
        "source_url": uuid.uuid4().hex,
        "agency_supplied": True,
        "supplying_entity": uuid.uuid4().hex,
        "agency_originated": True,
        "agency_aggregation": AgencyAggregation.FEDERAL.value,
        "coverage_start": "2020-01-01",
        "coverage_end": "2020-12-31",
        "detail_level": DetailLevel.INDIVIDUAL.value,
        "access_types": [
            AccessType.API.value,
            AccessType.WEB_PAGE.value,
            AccessType.DOWNLOAD.value,
        ],
        "data_portal_type": uuid.uuid4().hex,
        "record_formats": [uuid.uuid4().hex, uuid.uuid4().hex],
        "update_method": UpdateMethod.INSERT.value,
        "tags": [uuid.uuid4().hex, uuid.uuid4().hex],
        "readme_url": uuid.uuid4().hex,
        "originating_entity": uuid.uuid4().hex,
        "retention_schedule": RetentionSchedule.ONE_TO_TEN_YEARS.value,
        "rejection_note": uuid.uuid4().hex,
        "scraper_url": uuid.uuid4().hex,
        "submission_notes": uuid.uuid4().hex,
        "submitter_contact_info": uuid.uuid4().hex,
        "agency_described_not_in_database": uuid.uuid4().hex,
        "data_portal_type_other": uuid.uuid4().hex,
        "access_notes": uuid.uuid4().hex,
        "url_status": URLStatus.OK.value,
        "record_type_name": RecordTypes.ARREST_RECORDS.value,
    }

    tdc.request_validator.update_data_source(
        tus=tdc.get_admin_tus(),
        data_source_id=cdr.id,
        entry_data=entry_data,
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=DataSourcesByIDGetEndpointSchemaConfig.primary_output_schema,
    )

    data = response_json["data"]
    assert_contains_key_value_pairs(
        dict_to_check=data,
        key_value_pairs=entry_data,
    )

    # Test that last_approval_editor is None
    assert data["last_approval_editor"] is None
