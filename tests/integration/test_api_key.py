"""Integration tests for /api_key endpoint"""

from middleware.api_key import ApiKey
from resources.ApiKeyResource import API_KEY_ROUTE
from resources.endpoint_schema_config import SchemaConfigs
from tests.conftest import dev_db_client, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_db_client,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_api_key_post(flask_client_with_db, dev_db_client):
    """
    Test that GET call to /api_key endpoint successfully creates an API key and aligns it with the user's API key in the database
    """

    user_info = create_test_user_db_client(dev_db_client)

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=f"/auth{API_KEY_ROUTE}",
        json={"email": user_info.email, "password": user_info.password},
        expected_schema=SchemaConfigs.API_KEY_POST.value.primary_output_schema,
    )

    # Check that API key aligned with user
    new_user_info = dev_db_client.get_user_info(user_info.email)
    api_key_raw = response_json.get("api_key")
    api_key = ApiKey(raw_key=api_key_raw)

    assert (
        new_user_info.api_key == api_key.key_hash
    ), "API key returned not aligned with user API key in database"
