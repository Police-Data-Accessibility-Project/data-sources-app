from enum import Enum

class PermissionsEnum(Enum):
    ADMIN = "admin"
    USER = "user"

class UserPermissions:

    def __init__(self):
        self.permissions = set()

    def add_permission(self, permission: PermissionsEnum):
        self.permissions.add(permission)

    def remove_permission(self, permission: PermissionsEnum):
        self.permissions.discard(permission)

    def has_permission(self, permission: PermissionsEnum) -> bool:
        return permission in self.permissions
