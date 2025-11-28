from endpoints.v3.permissions.get.response import (
    GetPermissionListResponse,
    PermissionDescriptionMapping,
)
from middleware.enums import PermissionsEnum
from middleware.schema_and_dto.dtos.common_dtos import MessageDTO
from tests.helpers.helper_classes.TestUserSetup import TestUserSetup
from tests.integration.v3.helpers.api_test_helper import APITestHelper


def test_permissions(api_test_helper: APITestHelper, user_standard: TestUserSetup):
    """
    Test the retrieval, addition, and removal of user permissions
    """
    ath = api_test_helper
    tus = user_standard

    rv = ath.request_validator

    response: GetPermissionListResponse = rv.get_v3(
        url="/permission",
        expected_model=GetPermissionListResponse,
    )
    assert response.mappings == []

    user_url: str = f"/permission/user/{tus.user_info.user_id}"

    user_get_response_1: GetPermissionListResponse = rv.get_v3(
        url=user_url,
        expected_model=GetPermissionListResponse,
    )
    assert user_get_response_1.mappings == []

    rv.post_v3(
        url=f"{user_url}/add",
        expected_model=MessageDTO,
        json={
            "permission": PermissionsEnum.DB_WRITE.value,
        },
    )

    user_get_response_2: GetPermissionListResponse = rv.get_v3(
        url=user_url,
        expected_model=GetPermissionListResponse,
    )
    assert user_get_response_2.mappings == [
        PermissionDescriptionMapping(
            permission=PermissionsEnum.DB_WRITE,
            description="Use endpoints that write data to the database.",
        )
    ]

    rv.post_v3(
        url=f"{user_url}/remove",
        expected_model=MessageDTO,
        json={
            "permission": PermissionsEnum.DB_WRITE.value,
        },
    )

    user_get_response_3: GetPermissionListResponse = rv.get_v3(
        url=user_url,
        expected_model=GetPermissionListResponse,
    )
    assert user_get_response_3.mappings == []
