from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_sources_by_id_delete(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that DELETE call to /data-sources-by-id/<data_source_id> endpoint successfully deletes the data source and verifies the change in the database
    """
    # Insert new entry
    tdc = test_data_creator_flask

    ds_info = tdc.data_source()

    result = tdc.db_client.get_data_source_by_id(
        data_source_id=int(ds_info.id),
        data_sources_columns=["id"],
        data_requests_columns=[],
    )
    assert result is not None

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="delete",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{ds_info.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
    )

    result = tdc.db_client.get_data_source_by_id(
        data_source_id=int(ds_info.id),
        data_sources_columns=["id"],
        data_requests_columns=[],
    )

    assert result is None
