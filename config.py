# Global configuration
import os

from authlib.integrations.flask_client import OAuth

from middleware.util import get_env_variable


class Config:
    connection = None

config = Config()

oauth = OAuth()
oauth.register(
    name="github",
    client_id=get_env_variable("GITHUB_CLIENT_ID"),
    client_secret=get_env_variable("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)