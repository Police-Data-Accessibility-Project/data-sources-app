import os
from datetime import timedelta, date, datetime

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from resources.Callback import namespace_auth
from resources.CreateUserWithGithub import namespace_create_user_with_github
from resources.DataRequests import namespace_data_requests
from resources.HomepageSearchCache import namespace_homepage_search_cache
from resources.LinkToGithub import namespace_link_to_github
from resources.LoginWithGithub import namespace_login_with_github
from resources.Permissions import namespace_permissions
from resources.Search import namespace_search
from resources.TypeaheadSuggestions import (
    namespace_typeahead_suggestions,
)
from flask_restx import Api

from config import config, oauth, limiter, jwt
from middleware.initialize_psycopg_connection import initialize_psycopg_connection
from resources.Agencies import namespace_agencies
from resources.ApiKey import namespace_api_key
from resources.Archives import namespace_archives
from resources.DataSources import namespace_data_source
from resources.Login import namespace_login
from resources.RefreshSession import namespace_refresh_session
from resources.RequestResetPassword import namespace_request_reset_password
from resources.ResetPassword import namespace_reset_password
from resources.ResetTokenValidation import namespace_reset_token_validation
from resources.UniqueURLChecker import namespace_url_checker
from resources.User import namespace_user_old
from resources.CreateTestUserWithElevatedPermissions import namespace_create_test_user
from resources.UserProfile import namespace_user

NAMESPACES = [
    namespace_api_key,
    namespace_request_reset_password,
    namespace_user_old,
    namespace_reset_token_validation,
    namespace_archives,
    namespace_agencies,
    namespace_data_source,
    namespace_login,
    namespace_refresh_session,
    namespace_reset_password,
    namespace_typeahead_suggestions,
    namespace_search,
    namespace_auth,
    namespace_link_to_github,
    namespace_login_with_github,
    namespace_create_user_with_github,
    namespace_permissions,
    namespace_create_test_user,
    namespace_data_requests,
    # Below should not be enabled until https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/458
    # namespace_homepage_search_cache,
    namespace_url_checker,
    namespace_user,
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


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, date) or isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def create_app() -> Flask:
    psycopg2_connection = initialize_psycopg_connection()
    config.connection = psycopg2_connection
    api = Api()
    for namespace in NAMESPACES:
        api.add_namespace(namespace)
    app = Flask(__name__)
    app.json = UpdatedJSONProvider(app)

    # JWT settings
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    app.secret_key = get_flask_app_cookie_encryption_key()
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    CORS(app)

    api.init_app(app)
    oauth.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"))
