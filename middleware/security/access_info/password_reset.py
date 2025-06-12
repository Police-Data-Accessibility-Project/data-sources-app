from middleware.enums import AccessTypeEnum
from middleware.security.access_info.base import AccessInfoBase


class PasswordResetTokenAccessInfo(AccessInfoBase):
    access_type: AccessTypeEnum = AccessTypeEnum.RESET_PASSWORD
    user_id: int
    user_email: str
    reset_token: str
