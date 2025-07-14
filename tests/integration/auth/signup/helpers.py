from http import HTTPStatus
from typing import Optional
from unittest.mock import MagicMock

from marshmallow import Schema

from db.enums import UserCapacityEnum
from endpoints.instantiations.auth_.signup.endpoint_schema_config import (
    AuthSignupEndpointSchemaConfig,
)
from endpoints.schema_config.instantiations.auth.login import LoginEndpointSchemaConfig
from tests.helper_scripts.common_test_data import get_test_email
from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)
from tests.helper_scripts.helper_functions_simple import get_authorization_header


class SignupTestHelper:
    def __init__(self, tdc: TestDataCreatorFlask, mocker):
        self.tdc = tdc
        self.request_validator = tdc.request_validator
        self.mocker = mocker
        self.email = get_test_email()
        self.password = "test_password"

    def patch(self, addr: str) -> MagicMock:
        return self.mocker.patch(addr)

    def patch_expiry(self, timestamp: int):
        self.mocker.patch(
            "endpoints.instantiations.auth_.signup.middleware._get_validation_expiry",
            return_value=timestamp,
        )

    def login(
        self,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Schema = LoginEndpointSchemaConfig.primary_output_schema,
    ):
        self.request_validator.login(
            email=self.email,
            password=self.password,
            expected_response_status=expected_response_status,
            expected_schema=expected_schema,
            expected_json_content=expected_json_content,
        )

    def signup_user(
        self,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        capacities: list[UserCapacityEnum] | None = None,
    ):
        mock = self.patch(
            "endpoints.instantiations.auth_.signup.middleware.send_signup_link"
        )
        self.request_validator.post(
            endpoint="/api/auth/signup",
            json={
                "email": self.email,
                "password": self.password,
                "capacities": [c.value for c in capacities] if capacities else None,
            },
            expected_schema=AuthSignupEndpointSchemaConfig.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )
        if expected_response_status != HTTPStatus.OK:
            return None
        return check_email_and_return_token(mock, self.email)

    def resend_validation_email(
        self,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        mock = self.patch(
            "endpoints.instantiations.auth_.resend_validation_email.middleware.send_signup_link"
        )
        self.request_validator.post(
            endpoint="/api/auth/resend-validation-email",
            json={"email": self.email},
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )
        if not expected_response_status == HTTPStatus.OK:
            return None
        return check_email_and_return_token(mock, self.email)

    def validate_email(
        self,
        token: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
    ):
        self.request_validator.post(
            endpoint="/api/auth/validate-email",
            headers=get_authorization_header(scheme="Bearer", token=token),
            json={"token": token},
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )


def check_email_and_return_token(mock, email: str):
    assert mock.call_args[1]["email"] == email
    return mock.call_args[1]["token"]
