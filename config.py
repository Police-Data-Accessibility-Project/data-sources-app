# Global configuration

from authlib.integrations.flask_client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

from middleware.util.env import get_env_variable
from psycopg.connection import Connection as PgConnection


class Config:
    connection: PgConnection = None


config = Config()

secret_key = get_env_variable("FLASK_APP_COOKIE_ENCRYPTION_KEY")
cache_secret_key = f"_state_github_{secret_key}"

oauth = OAuth()
oauth.register(
    name="github",
    client_id=get_env_variable("GH_CLIENT_ID"),
    client_secret=get_env_variable("GH_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

jwt = JWTManager()
