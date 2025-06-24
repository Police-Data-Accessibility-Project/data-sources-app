from endpoints.schema_config.instantiations.data_sources.by_id.agencies.get import (
    DataSourcesRelatedAgenciesGet,
)
from tests.helper_scripts.constants import (
    DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT,
    DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT,
)
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_source_by_id_related_agencies(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask

    # Create data source
    ds_info = tdc.data_source()

    # Confirm no agencies associated with data source yet

    def get_related_agencies():
        return run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT.format(
                data_source_id=ds_info.id
            ),
            headers=tdc.get_admin_tus().jwt_authorization_header,
            expected_schema=DataSourcesRelatedAgenciesGet.primary_output_schema,
        )

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 0
    assert json_data["metadata"]["count"] == 0

    # Create agency
    agency_info = tdc.agency()

    # Associate agency with data source
    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT.format(
            data_source_id=ds_info.id, agency_id=agency_info.id
        ),
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Confirm agency is associated with data source

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 1
    assert json_data["metadata"]["count"] == 1
    assert json_data["data"][0]["id"] == int(agency_info.id)

    # Delete association

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT.format(
            data_source_id=ds_info.id, agency_id=agency_info.id
        ),
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    # Confirm agency is no longer associated with data source

    json_data = get_related_agencies()
    assert len(json_data["data"]) == 0
    assert json_data["metadata"]["count"] == 0
