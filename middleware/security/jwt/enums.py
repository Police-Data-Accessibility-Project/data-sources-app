from enum import Enum, auto


class JWTPurpose(Enum):
    PASSWORD_RESET = auto()
    VALIDATE_EMAIL = auto()
    GITHUB_ACCESS_TOKEN = auto()
    STANDARD_ACCESS_TOKEN = auto()
    REFRESH_TOKEN = auto()
