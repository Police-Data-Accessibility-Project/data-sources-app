from http import HTTPStatus

from tests.helpers.constants import DATA_SOURCES_BASE_ENDPOINT
from tests.helpers.helper_classes.test_data_creator.flask import TestDataCreatorFlask
from tests.helpers.run_and_validate_request import run_and_validate_request


def test_data_sources_by_id_get_invalid_id(
    test_data_creator_flask: TestDataCreatorFlask,
):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()
    _ = run_and_validate_request(
        flask_client=tdc.flask_client,
        http_method="get",
        endpoint=f"{DATA_SOURCES_BASE_ENDPOINT}/99999",
        headers=tus.api_authorization_header,
        expected_response_status=HTTPStatus.NOT_FOUND,
    )
