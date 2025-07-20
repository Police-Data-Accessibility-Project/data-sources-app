from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_record_types_and_categories_get(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    response_json = tdc.request_validator.get_record_types_and_categories(
        headers=tdc.get_admin_tus().api_authorization_header
    )

    print(response_json)
    assert len(response_json) > 0
