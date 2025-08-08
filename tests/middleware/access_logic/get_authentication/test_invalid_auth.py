from unittest.mock import MagicMock

import pytest
from werkzeug.exceptions import BadRequest

from middleware.enums import AccessTypeEnum
from middleware.security.auth.header.model import HeaderAuthInfo
from middleware.security.auth.helpers import get_authentication
from middleware.security.auth.method_config.enums import AuthScheme
from tests.middleware.access_logic.get_authentication.constants import PATCH_ROOT


def test_get_authentication_invalid_auth(monkeypatch):
    mock = MagicMock(
        return_value=HeaderAuthInfo(
            auth_scheme=AuthScheme.BASIC,
            token="token",
        )
    )
    monkeypatch.setattr(f"{PATCH_ROOT}", mock)

    with pytest.raises(BadRequest):
        get_authentication(allowed_access_methods=[AccessTypeEnum.JWT])
