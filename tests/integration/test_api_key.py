"""Integration tests for /api_key endpoint"""

from middleware.api_key import ApiKey
from resources.ApiKeyResource import API_KEY_ROUTE
from resources.endpoint_schema_config import SchemaConfigs
from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_functions_complex import (
    create_test_user_db_client,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from conftest import test_data_creator_flask, monkeysession


def test_api_key_post(test_data_creator_flask: TestDataCreatorFlask):
    """
    Test that GET call to /api_key endpoint successfully creates an API key and aligns it with the user's API key in the database
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()

    response_json = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="post",
        endpoint=f"/auth{API_KEY_ROUTE}",
        headers=tus.jwt_authorization_header,
        expected_schema=SchemaConfigs.API_KEY_POST.value.primary_output_schema,
    )

    # Check that API key aligned with user
    new_user_info = tdc.db_client.get_user_info(tus.user_info.email)
    api_key_raw = response_json.get("api_key")
    api_key = ApiKey(raw_key=api_key_raw)

    assert (
        new_user_info.api_key == api_key.key_hash
    ), "API key returned not aligned with user API key in database"
