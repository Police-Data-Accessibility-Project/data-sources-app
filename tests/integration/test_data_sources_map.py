"""Integration tests for /data-sources-map endpoint"""

from db.enums import ApprovalStatus
from endpoints.schema_config.enums import SchemaConfigs
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)

from tests.conftest import test_data_creator_flask


# This endpoint no longer works because of the other data source endpoint
# It is interpreted as another data source id
# But we have not yet decided whether to modify or remove it entirely
def test_data_sources_map_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /data-sources-map endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
    """
    tdcf = test_data_creator_flask
    tdc = test_data_creator_flask.tdcdb
    tus = tdcf.standard_user()
    location_id = tdc.locality()
    ds_id = tdc.data_source(
        approval_status=ApprovalStatus.APPROVED, record_type_id=1
    ).id
    a_id = tdc.agency(
        location_id=location_id,
        lat=0.0,
        lng=0.0,
    ).id
    tdc.link_data_source_to_agency(
        data_source_id=ds_id,
        agency_id=a_id,
    )
    response_json = tdcf.request_validator.get(
        endpoint="/api/map/data-sources",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_MAP.value.primary_output_schema,
    )
    data = response_json["data"]
    assert len(data) > 0
    assert data[0]["location_id"] is not None
