import datetime
from http import HTTPStatus
from typing import Union, Optional

import jwt
from jwt import InvalidSignatureError
from werkzeug.exceptions import BadRequest

from middleware.flask_response_manager import FlaskResponseManager
from middleware.security.jwt.constants import ALGORITHM
from middleware.security.jwt.enums import JWTPurpose
from middleware.security.jwt.helpers import get_secret_key


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
            raise BadRequest(f"Invalid JWT Purpose: {decoded_purpose} != {purpose}")

    def is_expired(self):
        return self.exp < datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
