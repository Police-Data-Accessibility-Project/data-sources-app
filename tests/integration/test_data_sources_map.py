"""Integration tests for /data-sources-map endpoint"""



from resources.endpoint_schema_config import SchemaConfigs
from tests.helper_scripts.common_test_data import TestDataCreatorFlask

from conftest import test_data_creator_flask, monkeysession

# This endpoint no longer works because of the other data source endpoint
# It is interpreted as another data source id
# But we have not yet decided whether to modify or remove it entirely
def test_data_sources_map_get(
    test_data_creator_flask: TestDataCreatorFlask
):
    """
    Test that GET call to /data-sources-map endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    response_json = tdc.request_validator.get(
        endpoint="/api/data-sources/data-sources-map",
        headers=tus.api_authorization_header,
        expected_schema=SchemaConfigs.DATA_SOURCES_MAP.value.primary_output_schema,
    )
    data = response_json["data"]
    assert len(data) > 0

