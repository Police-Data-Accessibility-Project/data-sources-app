from http import HTTPStatus

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError

from middleware.flask_response_manager import FlaskResponseManager
from middleware.security.jwt.helpers import get_jwt_access_info_with_permissions
from middleware.security.jwt.core import SimpleJWT
from middleware.security.jwt.enums import JWTPurpose


class JWTService:
    @staticmethod
    def get_identity():
        try:
            verify_jwt_in_request()
            return get_jwt_identity()
        except NoAuthorizationError:
            FlaskResponseManager.abort(
                HTTPStatus.BAD_REQUEST, message="Token is missing"
            )
        except Exception as e:
            return None

    @staticmethod
    def get_access_info(token: str):
        try:
            simple_jwt = SimpleJWT.decode(
                token, expected_purpose=JWTPurpose.STANDARD_ACCESS_TOKEN
            )
        except Exception:
            return None
        return get_jwt_access_info_with_permissions(
            user_email=simple_jwt.other_claims["user_email"],
            user_id=int(simple_jwt.sub),
            permissions_raw_str=simple_jwt.other_claims["permissions"],
        )
