from middleware.enums import AccessTypeEnum
from middleware.security.auth.method_config.helpers import validate_refresh_token
from middleware.security.auth.method_config.handlers import (
    jwt_handler,
    api_key_handler,
    password_reset_handler,
    validate_email_handler,
)
from middleware.security.auth.method_config.core import AuthMethodConfig
from middleware.security.auth.method_config.enums import AuthScheme

AUTH_METHODS_MAP = {
    AccessTypeEnum.JWT: AuthMethodConfig(handler=jwt_handler, scheme=AuthScheme.BEARER),
    AccessTypeEnum.API_KEY: AuthMethodConfig(
        handler=api_key_handler, scheme=AuthScheme.BASIC
    ),
    AccessTypeEnum.RESET_PASSWORD: AuthMethodConfig(
        handler=password_reset_handler, scheme=AuthScheme.BEARER
    ),
    AccessTypeEnum.VALIDATE_EMAIL: AuthMethodConfig(
        handler=validate_email_handler, scheme=AuthScheme.BEARER
    ),
    AccessTypeEnum.REFRESH_JWT: AuthMethodConfig(
        handler=validate_refresh_token, scheme=AuthScheme.BEARER
    ),
}
