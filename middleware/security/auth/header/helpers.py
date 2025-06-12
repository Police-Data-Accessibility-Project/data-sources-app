from werkzeug.exceptions import BadRequest

from middleware.flask_response_manager import FlaskResponseManager
from middleware.security.access_logic import get_authorization_header_from_request
from middleware.security.auth.header.model import HeaderAuthInfo
from middleware.security.auth.method_config.enums import AuthScheme


def get_header_auth_info() -> HeaderAuthInfo:
    authorization_header = get_authorization_header_from_request()
    try:
        authorization_header_parts = authorization_header.split(" ")
        if len(authorization_header_parts) != 2:
            raise BadRequest("Improperly formatted authorization header")
        scheme_string = AuthScheme(authorization_header_parts[0])
        token = authorization_header_parts[1]
        return HeaderAuthInfo(auth_scheme=AuthScheme(scheme_string), token=token)
    except (ValueError, IndexError, AttributeError):
        raise BadRequest("Improperly formatted authorization header")
