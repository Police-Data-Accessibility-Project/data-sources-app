from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_get_spec(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    tdc.request_validator.get_api_spec()
