from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.conftest import test_data_creator_flask, monkeysession


def test_get_spec(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    tdc.request_validator.get_api_spec()
