from http import HTTPStatus

from middleware.enums import PermissionsEnum
from tests.helpers.helper_classes.test_data_creator.flask import (
    TestDataCreatorFlask,
)


def test_admin_user_create(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    # Create a new admin user
    new_user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "permissions": [
            PermissionsEnum.READ_ALL_USER_INFO.value,
            PermissionsEnum.DB_WRITE.value,
        ],
    }
    response = tdc.request_validator.create_user(
        headers=admin_tus.jwt_authorization_header,
        email=new_user_data["email"],
        password=new_user_data["password"],
        permissions=new_user_data["permissions"],
    )

    # Successfully log in as the new admin user
    tdc.request_validator.login(
        email=new_user_data["email"],
        password=new_user_data["password"],
    )

    # Delete the user
    tdc.request_validator.delete_user(
        headers=admin_tus.jwt_authorization_header,
        user_id=response["id"],
    )

    # Attempt to login as the deleted user and fail
    tdc.request_validator.login(
        email=new_user_data["email"],
        password=new_user_data["password"],
        expected_response_status=HTTPStatus.UNAUTHORIZED,
    )


def test_admin_user_get_all(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    # Create a few new admin users
    for i in range(3):
        tdc.request_validator.create_user(
            headers=admin_tus.jwt_authorization_header,
            email=f"newuser{i}@example.com",
            password="password123",
            permissions=[
                PermissionsEnum.READ_ALL_USER_INFO.value,
                PermissionsEnum.DB_WRITE.value,
            ],
        )

    # Get all admin users
    response = tdc.request_validator.get_users(
        headers=admin_tus.jwt_authorization_header,
    )
    assert len(response) >= 3

    data = response["data"]

    for i in range(3):
        assert "newuser" in data[i]["email"]
        assert data[i]["permissions"] in (
            [PermissionsEnum.READ_ALL_USER_INFO.value, PermissionsEnum.DB_WRITE.value],
            [PermissionsEnum.DB_WRITE.value, PermissionsEnum.READ_ALL_USER_INFO.value],
        )


def test_admin_user_update(test_data_creator_flask: TestDataCreatorFlask):
    tdc = test_data_creator_flask
    admin_tus = tdc.get_admin_tus()

    # Create a new admin user
    response = tdc.request_validator.create_user(
        headers=admin_tus.jwt_authorization_header,
        email="newuserput@example.com",
        password="password123",
        permissions=[
            PermissionsEnum.READ_ALL_USER_INFO.value,
            PermissionsEnum.DB_WRITE.value,
        ],
    )
    new_user_id = response["id"]

    # Update the new admin user
    tdc.request_validator.update_admin_user(
        headers=admin_tus.jwt_authorization_header,
        resource_id=new_user_id,
        password="newpassword123",
    )

    # Login as the updated admin user
    tdc.request_validator.login(
        email="newuserput@example.com",
        password="newpassword123",
    )
