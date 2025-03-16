# Global configuration
import os
from uuid import uuid4

from authlib.integrations.flask_client import OAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

from middleware.util import get_env_variable


class Config:
    connection = None


config = Config()

secret_key = get_env_variable("FLASK_APP_COOKIE_ENCRYPTION_KEY")
cache_secret_key = f"_state_github_{secret_key}"

is_production = os.environ.get('ENVIRONMENT') == 'production'
base_callback_url = "https://data-sources.pdap.io/api/auth/callback" if is_production else "https://data-sources.pdap.dev/api/auth/callback"

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
    client_kwargs={
        "scope": "user:email",
        "redirect_uri": base_callback_url
        },
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

jwt = JWTManager()
