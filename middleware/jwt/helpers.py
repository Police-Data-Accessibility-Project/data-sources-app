from middleware.jwt.enums import JWTPurpose
from middleware.util.env import get_env_variable


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
