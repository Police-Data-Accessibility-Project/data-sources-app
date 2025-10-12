from middleware.primary_resource_logic.unique_url_checker import (
    UniqueURLCheckerResponseOuterSchema,
)
from tests.helpers.complex_test_data_creation_functions import (
    create_data_source_entry_for_url_duplicate_checking,
)
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_unique_url_checker(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    ENDPOINT = "check/unique-url"
    header = admin_tus.api_authorization_header
    create_data_source_entry_for_url_duplicate_checking(tdc.db_client)

    # Happy path
    non_duplicate_url = "https://not-a-duplicate.com"
    run_and_validate_request(
        flask_client=tdc.flask_client,
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
            flask_client=tdc.flask_client,
            http_method="get",
            endpoint=ENDPOINT,
            query_parameters={"url": url},
            expected_json_content={
                "duplicates": [
                    {
                        "original_url": "https://duplicate-checker.com/",
                    }
                ]
            },
            expected_schema=UniqueURLCheckerResponseOuterSchema,
            headers=header,
        )
