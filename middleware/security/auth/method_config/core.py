from typing import Callable

from pydantic import BaseModel

from middleware.security.auth.method_config.enums import AuthScheme


class AuthMethodConfig(BaseModel):
    handler: Callable
    scheme: AuthScheme
