from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from middleware.enums import PermissionsEnum


class UserInfoNonSensitive(BaseModel):
    user_id: int
    email: str
    created_at: datetime
    updated_at: datetime


class UsersWithPermissions(UserInfoNonSensitive):
    permissions: list[PermissionsEnum]


class DataRequestInfoForGithub(BaseModel):
    """
    Data Request Info to be used in the creation of GitHub Issues
    """

    id: int
    title: str
    submission_notes: str
    data_requirements: str
    locations: Optional[list[str]]
