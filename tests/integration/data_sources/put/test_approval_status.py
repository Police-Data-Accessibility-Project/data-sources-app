from db.enums import ApprovalStatus
from endpoints.schema_config.instantiations.data_sources.by_id.get import (
    DataSourcesByIDGetEndpointSchemaConfig,
)
from tests.helper_scripts.common_asserts import assert_contains_key_value_pairs
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_sources_by_id_put_approval_status(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint
     successfully updates the last_approval_editor of the data source
     and verifies the change in the database
    """
    tdc = test_data_creator_flask
    tdc.clear_test_data()
    cdr = tdc.tdcdb.data_source(approval_status=ApprovalStatus.PENDING)

    entry_data = {"approval_status": ApprovalStatus.APPROVED.value}

    run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="put",
        endpoint=f"/api/data-sources/{cdr.id}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        json={"entry_data": entry_data},
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

    # Test that last_approval_editor is the user
    assert data["last_approval_editor"] == tdc.get_admin_tus().user_info.user_id
