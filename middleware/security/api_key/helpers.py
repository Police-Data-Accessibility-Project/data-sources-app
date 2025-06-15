from werkzeug.exceptions import BadRequest

from middleware.exceptions import InvalidAPIKeyException
from middleware.security.access_logic import get_authorization_header_from_request
from middleware.security.auth.method_config.enums import AuthScheme


def get_token_from_request_header(scheme: AuthScheme):
    authorization_header = get_authorization_header_from_request()
    return get_key_from_authorization_header(authorization_header, scheme=scheme.value)


def get_key_from_authorization_header(
    authorization_header: str, scheme: str = "Basic"
) -> str:
    try:
        authorization_header_parts = authorization_header.split(" ")
        if len(authorization_header_parts) != 2:
            raise BadRequest("Improperly formatted authorization header")
        if authorization_header_parts[0] != scheme:
            raise InvalidAPIKeyException
        return authorization_header_parts[1]
    except (ValueError, IndexError, AttributeError):
        raise InvalidAPIKeyException
