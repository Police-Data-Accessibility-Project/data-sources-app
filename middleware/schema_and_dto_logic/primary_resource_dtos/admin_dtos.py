from dataclasses import dataclass
from typing import Optional


@dataclass
class AdminUserPostDTO:
    email: str
    password: str
    permissions: list[str]


@dataclass
class AdminUserPutDTO:
    password: Optional[str] = None
    permissions: Optional[list[str]] = None
