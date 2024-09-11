from dataclasses import dataclass
from typing import Optional


@dataclass
class UserInfo:
    email: str
    password: str
    user_id: Optional[str] = None
