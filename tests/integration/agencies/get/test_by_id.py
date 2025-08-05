from endpoints.schema_config.instantiations.agencies.by_id.get import (
    AgenciesByIDGetEndpointSchemaConfig,
)
from tests.helpers.constants import AGENCIES_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_agencies_get_by_id(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /agencies/<id> endpoint properly retrieves the correct data
    """
    tdc = test_data_creator_flask

    location_id_1 = tdc.locality()
    location_id_2 = tdc.locality()

    # Add data via db client
    agency_id = tdc.agency(
        location_ids=[location_id_1, location_id_2],
    ).id

    # link agency id to data source
    cds = tdc.data_source()
    tdc.link_data_source_to_agency(data_source_id=cds.id, agency_id=agency_id)

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=AGENCIES_BASE_ENDPOINT + f"/{agency_id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=AgenciesByIDGetEndpointSchemaConfig.primary_output_schema,
    )

    data = response_json["data"]
    assert data["name"] == data["submitted_name"]
    assert data["id"] == int(agency_id)
    assert data["data_sources"][0]["id"] == int(cds.id)

    assert data["locations"][0]["location_id"] in (
        int(location_id_2),
        int(location_id_1),
    )
    assert data["locations"][1]["location_id"] in (
        int(location_id_2),
        int(location_id_1),
    )
