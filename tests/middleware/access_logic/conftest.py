import pytest

from tests.middleware.access_logic.mocks.get_access_info_from_jwt_or_api_key import (
    GetAccessInfoFromJWTOrAPIKeyMocks,
)


@pytest.fixture
def get_access_info_mocks():
    return GetAccessInfoFromJWTOrAPIKeyMocks(
        patch_root="middleware.access_logic",
    )
