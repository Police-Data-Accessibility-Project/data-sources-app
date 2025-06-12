from pydantic import BaseModel

from middleware.security.auth.method_config.enums import AuthScheme


class HeaderAuthInfo(BaseModel):
    auth_scheme: AuthScheme
    token: str
