# Global configuration
import os

from authlib.integrations.flask_client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from middleware.util import get_env_variable


class Config:
    connection = None


config = Config()

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
