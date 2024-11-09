import datetime

import jwt

from middleware.util import get_env_variable

SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
ALGORITHM = "HS256"

class SimpleJWT:

    def __init__(
        self,
        sub: str,
        exp: float
    ):
        self.sub = sub
        self.exp = exp


    def encode(self):
        payload = {
            "sub": self.sub,
            "exp": self.exp
        }
        return jwt.encode(
            payload=payload,
            key=SECRET_KEY,
            algorithm=ALGORITHM
        )

    @staticmethod
    def decode(token):
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return SimpleJWT(
            sub=payload["sub"],
            exp=payload["exp"],
        )

    def is_expired(self):
        return self.exp < datetime.datetime.now(tz=datetime.timezone.utc).timestamp()

