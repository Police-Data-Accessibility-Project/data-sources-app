import urllib.parse

from endpoints.schema_config.instantiations.data_sources.get_many import (
    DataSourcesGetManyEndpointSchemaConfig,
)
from tests.helper_scripts.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_data_sources_get_many_limit_columns(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that GET call to /data-sources endpoint properly limits by columns
     when passed the `requested_columns` query parameter
    """
    tdc = test_data_creator_flask
    tdc.data_source()

    tus = tdc.standard_user()
    allowed_columns = ["name", "id"]
    url_encoded_column_string = urllib.parse.quote_plus(str(allowed_columns))
    expected_schema = DataSourcesGetManyEndpointSchemaConfig.primary_output_schema
    expected_schema.only = [
        "message",
        "metadata",
        "data.name",
        "data.id",
    ]
    expected_schema.partial = True

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}?page=1&requested_columns={url_encoded_column_string}",
        headers=tus.api_authorization_header,
        expected_schema=expected_schema,
    )
    data = response_json["data"]

    entry = data[0]
    for column in allowed_columns:
        assert column in entry
