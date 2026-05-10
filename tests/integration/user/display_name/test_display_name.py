"""Integration tests for the user `display_name` property (issue #875)."""

import uuid
from http import HTTPStatus

import pytest

from db.models.implementations.core.user.core import User
from middleware.schema_and_dto.dtos.user.display_name import (
    DISPLAY_NAME_CHARSET_MESSAGE,
    DISPLAY_NAME_DUPLICATE_MESSAGE,
    DISPLAY_NAME_LENGTH_MESSAGE,
    default_display_name_for_user_id,
)
from tests.integration.auth.signup.helpers import SignupTestHelper


def _unique_display_name(prefix: str = "dn") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def helper(test_data_creator_flask, mocker):
    return SignupTestHelper(test_data_creator_flask, mocker)


def _signup_with_display_name(
    helper: SignupTestHelper, display_name: str | None
) -> str:
    """Run the signup + validate-email flow and return the email used."""
    mock = helper.patch(
        "endpoints.instantiations.auth_.signup.middleware.send_signup_link"
    )
    helper.tdc.request_validator.post(
        endpoint="/auth/signup",
        json={
            "email": helper.email,
            "password": helper.password,
            "display_name": display_name,
        },
        expected_response_status=HTTPStatus.OK,
    )
    token = mock.call_args[1]["token"]
    helper.validate_email(token=token)
    return helper.email


def _get_display_name_from_db(tdc, email: str) -> str:
    db_client = tdc.db_client
    rows = db_client.get_all(User)
    for row in rows:
        if row["email"] == email:
            return row["display_name"]
    raise AssertionError(f"User with email {email} not found")


def test_signup_with_display_name_persists_it(helper):
    """A display_name supplied at signup should be saved on the created user."""
    chosen = _unique_display_name("alice")
    email = _signup_with_display_name(helper, chosen)

    assert _get_display_name_from_db(helper.tdc, email) == chosen


def test_signup_without_display_name_defaults_to_padded_user_id(helper):
    """When no display_name is supplied, default to the user's id (left-padded)."""
    email = _signup_with_display_name(helper, display_name=None)

    db_client = helper.tdc.db_client
    user_id = db_client.get_user_id(email=email)
    assert user_id is not None
    assert _get_display_name_from_db(helper.tdc, email) == (
        default_display_name_for_user_id(user_id)
    )


def test_signup_rejects_display_name_too_short(helper):
    helper.tdc.request_validator.post(
        endpoint="/auth/signup",
        json={
            "email": helper.email,
            "password": helper.password,
            "display_name": "ab",
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": DISPLAY_NAME_LENGTH_MESSAGE},
    )


def test_signup_rejects_display_name_too_long(helper):
    helper.tdc.request_validator.post(
        endpoint="/auth/signup",
        json={
            "email": helper.email,
            "password": helper.password,
            "display_name": "x" * 31,
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": DISPLAY_NAME_LENGTH_MESSAGE},
    )


def test_signup_rejects_display_name_with_invalid_characters(helper):
    helper.tdc.request_validator.post(
        endpoint="/auth/signup",
        json={
            "email": helper.email,
            "password": helper.password,
            "display_name": "has space",
        },
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": DISPLAY_NAME_CHARSET_MESSAGE},
    )


def test_signup_rejects_duplicate_display_name_case_insensitive(
    test_data_creator_flask, mocker
):
    """A second signup that requests an existing name (in different casing)
    should be rejected with a clear conflict message."""
    helper_a = SignupTestHelper(test_data_creator_flask, mocker)
    chosen = _unique_display_name("Bob")
    _signup_with_display_name(helper_a, chosen)

    helper_b = SignupTestHelper(test_data_creator_flask, mocker)
    helper_b.tdc.request_validator.post(
        endpoint="/auth/signup",
        json={
            "email": helper_b.email,
            "password": helper_b.password,
            "display_name": chosen.upper(),
        },
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={"message": DISPLAY_NAME_DUPLICATE_MESSAGE},
    )


def test_patch_updates_display_name(test_data_creator_flask):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    new_name = _unique_display_name("renamed")
    tdc.request_validator.patch(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
        json={"display_name": new_name},
    )

    assert _get_display_name_from_db(tdc, tus.user_info.email) == new_name


def test_patch_rejects_display_name_too_short(test_data_creator_flask):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    tdc.request_validator.patch(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
        json={"display_name": "ab"},
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": DISPLAY_NAME_LENGTH_MESSAGE},
    )


def test_patch_rejects_display_name_with_invalid_characters(test_data_creator_flask):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    tdc.request_validator.patch(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
        json={"display_name": "no spaces!"},
        expected_response_status=HTTPStatus.BAD_REQUEST,
        expected_json_content={"message": DISPLAY_NAME_CHARSET_MESSAGE},
    )


def test_patch_rejects_duplicate_display_name_case_insensitive(test_data_creator_flask):
    tdc = test_data_creator_flask
    user_a = tdc.standard_user()
    user_b = tdc.standard_user()

    chosen = _unique_display_name("taken")
    tdc.request_validator.patch(
        endpoint=f"/user/{user_a.user_id}",
        headers=user_a.jwt_authorization_header,
        json={"display_name": chosen},
    )

    tdc.request_validator.patch(
        endpoint=f"/user/{user_b.user_id}",
        headers=user_b.jwt_authorization_header,
        json={"display_name": chosen.upper()},
        expected_response_status=HTTPStatus.CONFLICT,
        expected_json_content={"message": DISPLAY_NAME_DUPLICATE_MESSAGE},
    )


def test_patch_allows_setting_same_display_name_idempotently(test_data_creator_flask):
    """Patching a user with the value they already have should not error."""
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    chosen = _unique_display_name("self")
    tdc.request_validator.patch(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
        json={"display_name": chosen},
    )
    # Repeat with the same value.
    tdc.request_validator.patch(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
        json={"display_name": chosen},
    )

    assert _get_display_name_from_db(tdc, tus.user_info.email) == chosen


def test_user_profile_response_includes_display_name(test_data_creator_flask):
    tdc = test_data_creator_flask
    tus = tdc.standard_user()

    response = tdc.request_validator.get(
        endpoint=f"/user/{tus.user_id}",
        headers=tus.jwt_authorization_header,
    )
    payload = response["data"] if "data" in response else response
    assert "display_name" in payload
    assert isinstance(payload["display_name"], str)
    assert len(payload["display_name"]) >= 3
