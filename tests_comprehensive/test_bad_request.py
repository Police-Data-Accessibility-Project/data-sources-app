"""
All the tests in this file are expected to produce a BAD_REQUEST response
"""

import pytest
from http import HTTPStatus

from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helpers.run_and_validate_request import run_and_validate_request
from tests_comprehensive.helper_scripts.SpecManager import SpecManager


def test_bad_request_endpoints_with_headers_have_bad_request_response_spec(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    All endpoints that require a header should have a BAD REQUEST response,
    listed in the documentation
    """
    tdc = test_data_creator_flask
    spec: dict = tdc.request_validator.get_api_spec()
    sm = SpecManager(spec)
    for method_info in sm.get_methods_with_any_header():
        if not method_info.has_response(HTTPStatus.BAD_REQUEST):
            raise AssertionError(
                f"""{method_info} should have a BAD REQUEST response."""
            )


def test_bad_request_malformed_header(test_data_creator_flask: TestDataCreatorFlask):
    """
    All endpoints which expect a header should produce a BAD REQUEST result when
    the header is malformed
    """
    tdc = test_data_creator_flask
    spec: dict = tdc.request_validator.get_api_spec()

    sm = SpecManager(spec)
    for method_info in sm.get_methods_with_any_header():
        print(f"Testing method {method_info}.")
        try:
            run_and_validate_request(
                flask_client=tdc.flask_client,
                http_method=method_info.method.value,
                endpoint=method_info.pathname(),
                headers={"Authorization": "bad"},
                expected_response_status=HTTPStatus.BAD_REQUEST,
            )
        except AssertionError as e:
            raise AssertionError(f"Error in method {method_info}: {e}")


def test_bad_request_missing_header(test_data_creator_flask: TestDataCreatorFlask):
    """
    All endpoints which expect a header should produce a BAD REQUEST result when
    the header is missing
    """
    tdc = test_data_creator_flask
    spec: dict = tdc.request_validator.get_api_spec()
    sm = SpecManager(spec)
    for method_info in sm.get_methods_with_any_header():
        try:
            print(f"Testing method {method_info}.")
            run_and_validate_request(
                flask_client=tdc.flask_client,
                http_method=method_info.method.value,
                endpoint=method_info.pathname(),
                headers={},
                expected_response_status=HTTPStatus.BAD_REQUEST,
            )
        except Exception as e:
            raise AssertionError(f"Error in method {method_info}: {e}")


def test_bad_request_jwt_not_allowed(test_data_creator_flask: TestDataCreatorFlask):
    """
    All endpoints where a JWT (aka, "Bearer" auth) is not listed as an option
    in the documentation should produce a BAD REQUEST result when a jwt is included
    """
    tdc = test_data_creator_flask
    spec: dict = tdc.request_validator.get_api_spec()
    sm = SpecManager(spec)
    tus = tdc.standard_user()
    for method_info in sm.get_methods_with_specific_header("Basic"):
        # Some methods have both basic and bearer, so exclude these
        if method_info.has_authorization_header("Bearer"):
            continue

        print(f"Testing method {method_info}.")
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method=method_info.method.value,
            endpoint=method_info.pathname(),
            headers=tus.jwt_authorization_header,
            expected_response_status=HTTPStatus.BAD_REQUEST,
        )


def test_bad_request_api_key_not_allowed(test_data_creator_flask: TestDataCreatorFlask):
    """
    All endpoints where an API key (aka, "Basic" auth) is not listed as an option
    in the documentation should produce either a FORBIDDEN result
    or a BAD REQUEST result when an api key is included
    """
    tdc = test_data_creator_flask
    spec: dict = tdc.request_validator.get_api_spec()
    sm = SpecManager(spec)
    tus = tdc.standard_user()
    for method_info in sm.get_methods_with_specific_header("Bearer"):
        # Some methods have both basic and bearer, so exclude these
        if method_info.has_authorization_header("Basic"):
            continue

        print(f"Testing method {method_info}.")
        run_and_validate_request(
            flask_client=tdc.flask_client,
            http_method=method_info.method.value,
            endpoint=method_info.pathname(),
            headers=tus.api_authorization_header,
            expected_response_status=HTTPStatus.BAD_REQUEST,
        )


def test_bad_request_invalid_types():
    """
    Test that fields which expect a certain type produce an expected
    BAD_REQUEST validation error when an incorrect type is produced
    For example:
    - integer expected, but string given
    - datetime expected, but date given
    - datetime expected, but string given
    - date expected, but datetime given
    - enum expected, but invalid string given
    """
    pytest.fail("Not implemented")


def test_bad_request_missing_required_fields():
    """
    Endpoints should return a BAD_REQUEST if a required field is missing
    If an endpoint has multiple required fields, each should be individually tested
    """
    pytest.fail("Not implemented")


def test_bad_request_negative_numbers():
    """
    For all endpoints which accept a number in the request body,
    negative numbers should be rejected with a BAD_REQUEST error
    """
    pytest.fail("Not implemented")


def test_bad_request_string_length():
    """
    Test that a bad request is returned when the string is too long
    """
    pytest.fail("Not implemented")


def test_bad_request_extra_fields():
    """
    For json requests, extra fields should either be ignored or, ideally, produce
    a validation error
    """
    pytest.fail("Not implemented")


def test_bad_request_endpoints_disallow_out_of_spec_json_inputs():
    """
    Endpoints which accept json inputs should not allow inputs which are
    not defined in the schema
    """
    pytest.fail("Not implemented")
