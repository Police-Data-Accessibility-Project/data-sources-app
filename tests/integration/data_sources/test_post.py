from endpoints.schema_config.instantiations.data_sources.by_id.get import (
    DataSourcesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.post import (
    DataSourcesPostEndpointSchemaConfig,
)
from endpoints.instantiations.data_sources_._shared.schemas.expanded import (
    DataSourceExpandedSchema,
)
from middleware.third_party_interaction_logic.mailgun_.constants import OPERATIONS_EMAIL
from tests.helpers.asserts import assert_contains_key_value_pairs
from tests.helpers.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helpers.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_data_sources_post(
    test_data_creator_flask: TestDataCreatorFlask, mock_send_via_mailgun
):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    agency_id = tdc.agency().id

    entry_data = generate_test_data_from_schema(
        schema=DataSourceExpandedSchema(
            exclude=[
                "id",
                "updated_at",
                "created_at",
                "record_type_id",
                "broken_source_url_as_of",
                "approval_status_updated_at",
                "last_approval_editor",
                "last_approval_editor_old",
            ],
        ),
    )

    response_json = tdc.request_validator.post(
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}",
        headers=tus.jwt_authorization_header,
        json={
            "entry_data": entry_data,
            "linked_agency_ids": [agency_id],
        },
        expected_schema=DataSourcesPostEndpointSchemaConfig.primary_output_schema,
    )

    mock_send_via_mailgun.assert_called_once_with(
        to_email=OPERATIONS_EMAIL,
        subject=f"New data source submitted: {entry_data['name']}",
        text=f"Description: \n\n{entry_data['description']}",
    )

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/{response_json['id']}",
        headers=tdc.get_admin_tus().jwt_authorization_header,
        expected_schema=DataSourcesByIDGetEndpointSchemaConfig.primary_output_schema,
    )

    assert_contains_key_value_pairs(
        dict_to_check=response_json["data"],
        key_value_pairs=entry_data,
    )

    agencies = response_json["data"]["agencies"]
    assert len(agencies) == 1
    assert agencies[0]["id"] == int(agency_id)
