from datetime import datetime

from pydantic import BaseModel

from middleware.enums import PermissionsEnum


class UserInfoNonSensitive(BaseModel):
    user_id: int
    email: str
    created_at: datetime
    updated_at: datetime


class UsersWithPermissions(UserInfoNonSensitive):
    permissions: list[PermissionsEnum]
