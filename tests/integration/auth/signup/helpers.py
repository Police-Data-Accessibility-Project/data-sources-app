from http import HTTPStatus
from typing import Optional

from endpoints.instantiations.auth_.signup.endpoint_schema_config import AuthSignupEndpointSchemaConfig
from tests.helper_scripts.helper_classes.RequestValidator import RequestValidator
from tests.helper_scripts.helper_functions_simple import get_authorization_header

def patch_send_signup_link(mocker):
    mock = mocker.patch(
        "endpoints.instantiations.auth_.signup.middleware.send_signup_link"
    )
    return mock

def check_email_and_return_token(mock, email: str):
    assert mock.call_args[1]["email"] == email
    return mock.call_args[1]["token"]


def signup_user(
    request_validator: RequestValidator,
    email: str,
    password: str,
    mocker,
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_json_content: Optional[dict] = None,
):
    mock = mocker.patch(
        "endpoints.instantiations.auth_.signup.middleware.send_signup_link"
    )
    request_validator.post(
            endpoint="/api/auth/signup",
            json={"email": email, "password": password},
            expected_schema=AuthSignupEndpointSchemaConfig.primary_output_schema,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
        )
    if expected_response_status != HTTPStatus.OK:
        return None
    return check_email_and_return_token(mock, email)

def resend_validation_email(
    request_validator: RequestValidator,
    email: str,
    mocker,
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_json_content: Optional[dict] = None,
):
    mock = mocker.patch(
        "endpoints.instantiations.auth_.resend_validation_email.middleware.send_signup_link"
    )
    request_validator.post(
        endpoint="/api/auth/resend-validation-email",
        json={"email": email},
        expected_response_status=expected_response_status,
        expected_json_content=expected_json_content,
    )
    if not expected_response_status == HTTPStatus.OK:
        return None
    return check_email_and_return_token(mock, email)


def validate_email(
    request_validator: RequestValidator,
    token: str,
    expected_response_status: HTTPStatus = HTTPStatus.OK,
    expected_json_content: Optional[dict] = None,
):
    request_validator.post(
        endpoint="/api/auth/validate-email",
        headers=get_authorization_header(scheme="Bearer", token=token),
        json={"token": token},
        expected_response_status=expected_response_status,
        expected_json_content=expected_json_content,
    )

