from middleware.enums import AccessTypeEnum
from middleware.security.access_info.base import AccessInfoBase


class RefreshAccessInfo(AccessInfoBase):
    access_type: AccessTypeEnum = AccessTypeEnum.REFRESH_JWT
    user_email: str
