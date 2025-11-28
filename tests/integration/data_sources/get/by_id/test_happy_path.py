"""Integration tests for /data-sources endpoint"""

from endpoints.instantiations.data_sources_.get.by_id.schema_config import (
    DataSourcesByIDGetEndpointSchemaConfig,
)

from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request
from tests.helpers.constants import (
    DATA_SOURCES_BASE_ENDPOINT,
)


def test_data_sources_by_id_get(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint
    retrieves the data source with the correct homepage URL
    """
    tdc = test_data_creator_flask
    tdc.clear_test_data()

    tus = tdc.standard_user()
    cds = tdc.data_source()

    # Create agency and link to data source
    agency_id = tdc.agency().id
    tdc.link_data_source_to_agency(data_source_id=cds.id, agency_id=agency_id)

    # Create data request and link to data source
    request_id = tdc.tdcdb.data_request(tus.user_info.user_id).id
    tdc.link_data_request_to_data_source(
        data_source_id=cds.id, data_request_id=request_id
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{cds.id}",
        headers=tus.api_authorization_header,
        expected_schema=DataSourcesByIDGetEndpointSchemaConfig.primary_output_schema,
    )

    data = response_json["data"]
    assert data["name"] == cds.name
    assert data["data_requests"][0]["id"] == int(request_id)
    assert data["agencies"][0]["id"] == int(agency_id)
