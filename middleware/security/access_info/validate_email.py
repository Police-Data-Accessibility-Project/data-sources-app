from middleware.enums import AccessTypeEnum
from middleware.security.access_info.base import AccessInfoBase


class ValidateEmailTokenAccessInfo(AccessInfoBase):
    access_type: AccessTypeEnum = AccessTypeEnum.VALIDATE_EMAIL
    validate_email_token: str
