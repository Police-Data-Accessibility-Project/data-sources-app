from pydantic import BaseModel

from middleware.enums import PermissionsEnum


class UpdatePermissionRequest(BaseModel):
    permission: PermissionsEnum
