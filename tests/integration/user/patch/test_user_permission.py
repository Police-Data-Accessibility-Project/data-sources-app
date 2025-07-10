from unittest.mock import MagicMock

import pytest
from werkzeug.exceptions import BadRequest

from db.client.core import DatabaseClient
from db.enums import UserCapacityEnum
from endpoints.instantiations.user.by_id.patch.dto import UserPatchDTO
from endpoints.instantiations.user.by_id.patch.middleware import patch_user
from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary


def test_user_patch_user_permissions(monkeypatch):
    """
    Users can only use the patch endpoint if:
    - They have the USER_CREATE_UPDATE permission
    - They are the same user as the one being patched

    All others should receive a BAD REQUEST response
    """
    monkeypatch.setattr("endpoints.instantiations.user.by_id.patch.middleware.message_response", MagicMock())
    mock_db_client = MagicMock(spec=DatabaseClient)
    dto = UserPatchDTO(
        capacities=[
            UserCapacityEnum.POLICE,
            UserCapacityEnum.PUBLIC_OFFICIAL,
        ]
    )
    _fails_as_different_user(dto, mock_db_client)
    _succeeds_as_same_user(dto, mock_db_client)
    _succeeds_as_admin(dto, mock_db_client)


def _fails_as_different_user(dto, mock_db_client):
    with pytest.raises(BadRequest):
        patch_user(
            db_client=mock_db_client,
            access_info=AccessInfoPrimary(
                access_type=AccessTypeEnum.JWT,
                user_email="test_email",
                user_id=1,
                permissions=[],
            ),
            user_id=2,
            dto=dto,
        )


def _succeeds_as_admin(dto, mock_db_client):
    patch_user(
        db_client=mock_db_client,
        access_info=AccessInfoPrimary(
            access_type=AccessTypeEnum.JWT,
            user_email="test_email",
            user_id=1,
            permissions=[PermissionsEnum.USER_CREATE_UPDATE],
        ),
        user_id=2,
        dto=dto,
    )


def _succeeds_as_same_user(dto, mock_db_client):
    patch_user(
        db_client=mock_db_client,
        access_info=AccessInfoPrimary(
            access_type=AccessTypeEnum.JWT,
            user_email="test_email",
            user_id=1,
            permissions=[],
        ),
        user_id=1,
        dto=dto,
    )