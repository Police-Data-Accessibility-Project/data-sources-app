"""Integration tests for /map/data-sources endpoint"""

from db.enums import ApprovalStatus
from endpoints.instantiations.map.data_sources.schema_config import DataSourcesMapEndpointSchemaConfig
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_data_sources_map_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /map/data-sources endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
    """
    tdcf = test_data_creator_flask
    tdc = test_data_creator_flask.tdcdb
    tus = tdcf.standard_user()
    location_id = tdc.locality()
    ds_id = tdc.data_source(approval_status=ApprovalStatus.APPROVED).id
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
        expected_schema=DataSourcesMapEndpointSchemaConfig.primary_output_schema,
    )
    data = response_json["data"]
    assert len(data) > 0
    assert data[0]["location_id"] is not None
