import pytest
from werkzeug.exceptions import Forbidden

from middleware.enums import AccessTypeEnum, PermissionsEnum
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.method_config.helpers import (
    check_permissions_with_access_info,
)


@pytest.mark.parametrize(
    "access_info, permissions, raises_forbidden",
    (
        (
            AccessInfoPrimary(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            [PermissionsEnum.READ_ALL_USER_INFO],
            False,
        ),
        (
            AccessInfoPrimary(
                user_email="test_email",
                access_type=AccessTypeEnum.JWT,
                permissions=[PermissionsEnum.READ_ALL_USER_INFO],
            ),
            [PermissionsEnum.READ_ALL_USER_INFO, PermissionsEnum.DB_WRITE],
            True,
        ),
        (
            None,
            None,
            True,
        ),
    ),
)
def test_check_permissions_with_access_info(
    access_info, permissions, raises_forbidden, monkeypatch
):
    if raises_forbidden:
        with pytest.raises(Forbidden):
            check_permissions_with_access_info(access_info, permissions)
    else:
        check_permissions_with_access_info(access_info, permissions)
