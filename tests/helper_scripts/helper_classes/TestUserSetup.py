from dataclasses import dataclass
from typing import Optional

from tests.helper_scripts.helper_classes.UserInfo import UserInfo


@dataclass
class TestUserSetup:
    user_info: UserInfo
    api_key: str
    api_authorization_header: dict
    jwt_authorization_header: Optional[dict] = None
