from endpoints.instantiations.map.data.schema_config import LocationsDataEndpointSchemaConfig
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_map_data(
    test_data_creator_flask: TestDataCreatorFlask,
    pittsburgh_id
) -> None:
    # TODO: Incomplete
    pass
    # tdc = test_data_creator_flask
    # rv = tdc.request_validator
    #
    # agency_id = tdc.agency(location_ids=[pittsburgh_id]).id
    # data_source_id = tdc.data_source().id
    # tdc.link_data_source_to_agency(
    #     data_source_id=data_source_id, agency_id=agency_id
    # )
    # tdc.db_client.refresh_all_materialized_views()
    #
    #
    # tus = tdc.standard_user()
    # response = rv.get(
    #     endpoint="/map/data",
    #     headers=tus.api_authorization_header,
    #     expected_schema=LocationsDataEndpointSchemaConfig.primary_output_schema
    # )
    # print(response)