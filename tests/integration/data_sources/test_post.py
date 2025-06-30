from endpoints.schema_config.instantiations.data_sources.by_id.get import (
    DataSourcesByIDGetEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.data_sources.post import (
    DataSourcesPostEndpointSchemaConfig,
)
from middleware.schema_and_dto.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from tests.helper_scripts.common_asserts import assert_contains_key_value_pairs
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.SchemaTestDataGenerator import (
    generate_test_data_from_schema,
)
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_sources_post(
    test_data_creator_flask: TestDataCreatorFlask,
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
