from endpoints.instantiations.data_sources_.post.request_.endpoint_schema_config import (
    PostDataSourceRequestEndpointSchemaConfig,
)
from endpoints.instantiations.data_sources_.post.request_.model import (
    PostDataSourceOuterRequest,
    PostDataSourceRequest,
)
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask


def test_post_data_source(
    test_data_creator_flask: TestDataCreatorFlask, agency_id_1: int, agency_id_2: int
):
    test_data_creator_flask.request_validator.post(
        endpoint="/data-sources",
        headers=test_data_creator_flask.standard_user().jwt_authorization_header,
        json=PostDataSourceOuterRequest(
            entry_data=PostDataSourceRequest(
                source_url="https://www.example.com/",
                name="test",
                description="Test description",
            ),
            linked_agency_ids=[],
        ).model_dump(mode="json"),
        expected_schema=PostDataSourceRequestEndpointSchemaConfig.primary_output_schema,
    )
