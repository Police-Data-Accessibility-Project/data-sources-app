from database_client.database_client import DatabaseClient
from middleware.primary_resource_logic.unique_url_checker import (
    UniqueURLCheckerResponseOuterSchema,
)
from tests.conftest import (
    flask_client_with_db,
    live_database_client,
    integration_test_admin_setup,
)
from tests.helper_scripts.common_test_data import (
    create_data_source_entry_for_url_duplicate_checking,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request


def test_unique_url_checker(
    flask_client_with_db, live_database_client, integration_test_admin_setup
):
    ENDPOINT = "check/unique-url"
    header = integration_test_admin_setup.tus.api_authorization_header
    create_data_source_entry_for_url_duplicate_checking(live_database_client)

    # Happy path
    non_duplicate_url = "https://not-a-duplicate.com"
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=ENDPOINT,
        query_parameters={"url": non_duplicate_url},
        expected_json_content={"duplicates": []},
        expected_schema=UniqueURLCheckerResponseOuterSchema,
        headers=header,
    )

    # Add tests for multiple variants
    same_urls = [
        "http://duplicate-checker.com/",
        "https://www.duplicate-checker.com",
        "http://www.duplicate-checker.com/",
    ]
    for url in same_urls:
        run_and_validate_request(
            flask_client=flask_client_with_db,
            http_method="get",
            endpoint=ENDPOINT,
            query_parameters={"url": url},
            expected_json_content={
                "duplicates": [
                    {
                        "original_url": "https://duplicate-checker.com/",
                        "approval_status": "rejected",
                        "rejection_note": "Test rejection note",
                    }
                ]
            },
            expected_schema=UniqueURLCheckerResponseOuterSchema,
            headers=header,
        )
