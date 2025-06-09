import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Union, Optional

import jwt
from jwt import InvalidSignatureError

from middleware.flask_response_manager import FlaskResponseManager
from middleware.util.env import get_env_variable

ALGORITHM = "HS256"


class JWTPurpose(Enum):
    PASSWORD_RESET = auto()
    VALIDATE_EMAIL = auto()
    GITHUB_ACCESS_TOKEN = auto()
    STANDARD_ACCESS_TOKEN = auto()
    REFRESH_TOKEN = auto()


def get_secret_key(purpose: JWTPurpose):
    if purpose == JWTPurpose.PASSWORD_RESET:
        return get_env_variable("RESET_PASSWORD_SECRET_KEY")
    elif purpose == JWTPurpose.GITHUB_ACCESS_TOKEN:
        return get_env_variable("JWT_SECRET_KEY")
    elif purpose == JWTPurpose.VALIDATE_EMAIL:
        return get_env_variable("VALIDATE_EMAIL_SECRET_KEY")
    elif purpose == JWTPurpose.STANDARD_ACCESS_TOKEN:
        return get_env_variable("JWT_SECRET_KEY")
    else:
        raise Exception(f"Invalid JWT Purpose: {purpose}")


class SimpleJWT:

    def __init__(
        self, sub: Union[str, dict], exp: float, purpose: JWTPurpose, **other_claims
    ):
        self.sub = sub
        self.exp = exp
        self.purpose = purpose
        self.key = get_secret_key(purpose)
        self.other_claims = other_claims

    def encode(self):
        payload = {
            "sub": self.sub,
            "exp": self.exp,
        }
        payload.update(self.other_claims)
        return jwt.encode(
            payload=payload,
            key=self.key,
            algorithm=ALGORITHM,
            headers={"kid": str(self.purpose.value)},
        )

    @staticmethod
    def decode(token, expected_purpose: Optional[JWTPurpose] = None):
        kid = int(jwt.get_unverified_header(token)["kid"])
        decoded_purpose = JWTPurpose(kid)
        if expected_purpose is not None:
            SimpleJWT.validate_purpose(decoded_purpose, expected_purpose)
        try:
            payload = jwt.decode(
                jwt=token, key=get_secret_key(decoded_purpose), algorithms=[ALGORITHM]
            )
        except InvalidSignatureError as e:
            FlaskResponseManager.abort(code=HTTPStatus.UNAUTHORIZED, message=str(e))

        sub = payload["sub"]
        del payload["sub"]
        exp = payload["exp"]
        del payload["exp"]

        simple_jwt = SimpleJWT(
            sub=sub,
            exp=exp,
            purpose=decoded_purpose,
            **payload,
        )
        return simple_jwt

    @staticmethod
    def validate_purpose(decoded_purpose, purpose):
        if decoded_purpose != purpose:
            FlaskResponseManager.bad_request_abort(
                f"Invalid JWT Purpose: {decoded_purpose} != {purpose}"
            )

    def is_expired(self):
        return self.exp < datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
