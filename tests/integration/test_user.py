"""Integration tests for /user endpoint."""

from http import HTTPStatus
import uuid


from tests.helper_scripts.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_update_password(
    test_data_creator_flask: TestDataCreatorFlask,
):
    """
    Test that PUT call to endpoint successfully updates the user's password and verifies the new password hash is distinct from both the plain new password and the old password hash in the database
    """
    tdc = test_data_creator_flask

    tus = tdc.standard_user()
    old_password_hash = tdc.db_client.get_password_digest(tus.user_info.user_id)
    new_password = str(uuid.uuid4())

    def update_password(
        old_password: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
    ):
        return tdc.request_validator.update_password(
            headers=tus.jwt_authorization_header,
            old_password=old_password,
            new_password=new_password,
            expected_response_status=expected_response_status,
        )

    # Try to update password with different user and fail
    tus_other = tdc.standard_user()
    update_password(
        old_password=tus_other.user_info.password,
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    # Try to update password with incorrect old password and fail
    update_password(
        old_password="gibberish",
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )

    # Try to update password with correct old password and succeed
    update_password(
        old_password=tus.user_info.password,
    )

    new_password_hash = tdc.db_client.get_password_digest(tus.user_info.user_id)

    assert new_password != new_password_hash, (
        "Password and password hash should be distinct after password update"
    )
    assert new_password_hash != old_password_hash, (
        "Password hashes should be different on update"
    )
