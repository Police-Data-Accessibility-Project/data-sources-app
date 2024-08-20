import os
from datetime import timedelta

#import dotenv
from flask import Flask
from flask_cors import CORS

from resources.Callback import namespace_auth
from resources.CreateUserWithGithub import namespace_create_user_with_github
from resources.LinkToGithub import namespace_link_to_github
from resources.LoginWithGithub import namespace_login_with_github
from resources.Permissions import namespace_permissions
from resources.Search import namespace_search
from resources.TypeaheadSuggestions import (
    namespace_typeahead_suggestions,
)
from flask_restx import Api

from config import config, oauth, limiter, jwt
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
#from middleware.models import db
#from middleware.util import get_env_variable
from resources.Agencies import namespace_agencies
from resources.ApiKey import namespace_api_key
from resources.Archives import namespace_archives
from resources.DataSources import namespace_data_source
from resources.Login import namespace_login
from resources.QuickSearch import namespace_quick_search
from resources.RefreshSession import namespace_refresh_session
from resources.RequestResetPassword import namespace_request_reset_password
from resources.ResetPassword import namespace_reset_password
from resources.ResetTokenValidation import namespace_reset_token_validation
from resources.User import namespace_user
from resources.CreateTestUserWithElevatedPermissions import namespace_create_test_user

NAMESPACES = [
    namespace_api_key,
    namespace_request_reset_password,
    namespace_user,
    namespace_reset_token_validation,
    namespace_archives,
    namespace_agencies,
    namespace_data_source,
    namespace_login,
    namespace_refresh_session,
    namespace_reset_password,
    namespace_quick_search,
    namespace_typeahead_suggestions,
    namespace_search,
    namespace_auth,
    namespace_link_to_github,
    namespace_login_with_github,
    namespace_create_user_with_github,
    namespace_permissions,
    namespace_create_test_user
]

MY_PREFIX = "/api"


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = MY_PREFIX
        environ["SCRIPT_NAME"] = script_name
        path_info = environ["PATH_INFO"]
        if path_info.startswith(script_name):
            environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


def get_flask_app_cookie_encryption_key() -> str:
    return os.getenv("FLASK_APP_COOKIE_ENCRYPTION_KEY")

def create_app(testing=False) -> Flask:
    psycopg2_connection = initialize_psycopg2_connection()
    config.connection = psycopg2_connection
    api = Api()
    for namespace in NAMESPACES:
        api.add_namespace(namespace)
    app = Flask(__name__)

    # JWT settings
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    app.secret_key = get_flask_app_cookie_encryption_key()
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    CORS(app)
    '''dotenv.load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = get_env_variable(
        "DO_DATABASE_URL"
    )
    if testing is True:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_ECHO"] = True'''
    api.init_app(app)
    oauth.init_app(app)
    #db.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"))
