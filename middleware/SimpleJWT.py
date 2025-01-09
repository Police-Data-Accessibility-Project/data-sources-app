import datetime
from enum import Enum, auto
from http import HTTPStatus
from typing import Union

import jwt
from jwt import InvalidSignatureError

from middleware.flask_response_manager import FlaskResponseManager
from middleware.util import get_env_variable

ALGORITHM = "HS256"


class JWTPurpose(Enum):
    PASSWORD_RESET = auto()
    VALIDATE_EMAIL = auto()
    GITHUB_ACCESS_TOKEN = auto()
    STANDARD_ACCESS_TOKEN = auto()


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
        payload = {"sub": self.sub, "exp": self.exp, "purpose": self.purpose.value}
        payload.update(self.other_claims)
        return jwt.encode(payload=payload, key=self.key, algorithm=ALGORITHM)

    @staticmethod
    def decode(token, purpose: JWTPurpose):
        try:
            payload = jwt.decode(
                jwt=token, key=get_secret_key(purpose), algorithms=[ALGORITHM]
            )
        except InvalidSignatureError as e:
            FlaskResponseManager.abort(code=HTTPStatus.UNAUTHORIZED, message=str(e))
        purpose = JWTPurpose(payload["purpose"])
        del payload["purpose"]
        sub = payload["sub"]
        del payload["sub"]
        exp = payload["exp"]
        del payload["exp"]

        simple_jwt = SimpleJWT(
            sub=sub,
            exp=exp,
            purpose=purpose,
            **payload,
        )
        if simple_jwt.purpose != purpose:
            raise Exception(f"Invalid JWT Purpose: {simple_jwt.purpose} != {purpose}")
        return simple_jwt

    def is_expired(self):
        return self.exp < datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
