from pydantic import BaseModel

from middleware.enums import AccessTypeEnum


class AccessInfoBase(BaseModel):
    access_type: AccessTypeEnum
