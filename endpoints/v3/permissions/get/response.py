from pydantic import BaseModel

from middleware.enums import PermissionsEnum


class PermissionDescriptionMapping(BaseModel):
    permission: PermissionsEnum
    description: str


class GetPermissionListResponse(BaseModel):
    mappings: list[PermissionDescriptionMapping]
