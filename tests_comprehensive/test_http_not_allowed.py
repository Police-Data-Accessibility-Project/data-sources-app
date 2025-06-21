from http import HTTPStatus
from typing import Any

from tests.helper_scripts.helper_classes.TestDataCreatorFlask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests_comprehensive.helper_scripts.SpecManager import SpecManager

ALL_METHODS = ["get", "post", "put", "delete", "patch"]


def test_http_not_allowed(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask

    spec: dict[str, Any] = tdc.request_validator.get_api_spec()
    sm = SpecManager(spec)
    for path_info in sm.get_paths():
        for method in path_info.get_disallowed_methods():
            print(f"Testing method {method} on path {path_info.route_name}")
            run_and_validate_request(
                flask_client=tdc.flask_client,
                http_method=method.value,
                endpoint=path_info.route_name,
                expected_response_status=HTTPStatus.METHOD_NOT_ALLOWED,
            )
