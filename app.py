import os
from datetime import timedelta, date, datetime

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from middleware.SchedulerManager import SchedulerManager
from middleware.SimpleJWT import SimpleJWT
from middleware.scheduled_tasks.check_database_health import check_database_health
from middleware.util import get_env_variable
from resources.Admin import namespace_admin
from resources.Batch import namespace_bulk
from resources.Callback import namespace_auth
from resources.Contact import namespace_contact
from resources.DataRequests import namespace_data_requests
from resources.GithubDataRequests import namespace_github
from resources.LinkToGithub import namespace_link_to_github
from resources.Locations import namespace_locations
from resources.LoginWithGithub import namespace_login_with_github
from resources.Map import namespace_map
from resources.Match import namespace_match
from resources.Metadata import namespace_metadata
from resources.Metrics import namespace_metrics
from resources.Notifications import namespace_notifications
from resources.OAuth import namespace_oauth
from resources.Permissions import namespace_permissions
from resources.Search import namespace_search
from resources.Signup import namespace_signup
from resources.TypeaheadSuggestions import (
    namespace_typeahead_suggestions,
)
from flask_restx import Api

from config import config, oauth, limiter, jwt
from middleware.initialize_psycopg_connection import initialize_psycopg_connection
from resources.Agencies import namespace_agencies
from resources.ApiKeyResource import namespace_api_key
from resources.Archives import namespace_archives
from resources.DataSources import namespace_data_source
from resources.Login import namespace_login
from resources.RefreshSession import namespace_refresh_session
from resources.RequestResetPassword import namespace_request_reset_password
from resources.ResetPassword import namespace_reset_password
from resources.ResetTokenValidation import namespace_reset_token_validation
from resources.UniqueURLChecker import namespace_url_checker
from resources.CreateTestUserWithElevatedPermissions import namespace_create_test_user
from resources.UserProfile import namespace_user

NAMESPACES = [
    namespace_api_key,
    namespace_request_reset_password,
    namespace_oauth,
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
    namespace_permissions,
    namespace_create_test_user,
    namespace_data_requests,
    namespace_url_checker,
    namespace_user,
    namespace_github,
    namespace_notifications,
    namespace_map,
    namespace_signup,
    namespace_bulk,
    namespace_match,
    namespace_locations,
    namespace_metrics,
    namespace_admin,
    namespace_contact,
    namespace_metadata,
]

MY_PREFIX = "/api"


class WSGIMiddleware(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        self.set_up_reverse_proxy(environ)
        self.inject_user_id(environ)
        return self.app(environ, start_response)

    def set_up_reverse_proxy(self, environ):
        script_name = MY_PREFIX
        environ["SCRIPT_NAME"] = script_name
        path_info = environ["PATH_INFO"]
        if path_info.startswith(script_name):
            environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme

    def inject_user_id(self, environ):
        auth_header = environ.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :]
            my_jwt = SimpleJWT.decode(token)
            try:
                environ["HTTP_X_USER_ID"] = my_jwt.other_claims["user_id"]
                return
            except KeyError:
                pass

        environ["HTTP_X_USER_ID"] = "-"


def get_flask_app_cookie_encryption_key() -> str:
    return get_env_variable("FLASK_APP_COOKIE_ENCRYPTION_KEY")


class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, date) or isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def create_app() -> Flask:
    psycopg2_connection = initialize_psycopg_connection()
    config.connection = psycopg2_connection
    api = get_api_with_namespaces()
    app = Flask(__name__)
    app.json = UpdatedJSONProvider(app)

    # JWT settings
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)

    # Other configuration settings
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    app.secret_key = get_flask_app_cookie_encryption_key()
    app.wsgi_app = WSGIMiddleware(app.wsgi_app)
    CORS(app)

    api.init_app(app)
    oauth.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # Initialize and start the scheduler
    scheduler = SchedulerManager(app)
    scheduler.add_job(
        "database_health_check", check_database_health, minutes=60, delay_minutes=3
    )
    scheduler.start()

    # Store scheduler in the app context to manage it later
    app.scheduler = scheduler

    return app


def get_api_with_namespaces():
    api = Api(
        version="2.0",
        title="PDAP Data Sources API",
        description="The following is the API documentation for the PDAP Data Sources API."
        "\n\nFor API help, consult [our getting started guide.](https://docs.pdap.io/api/introduction)"
        "\n\nTo search the database, go to [pdap.io](https://pdap.io).",
    )
    for namespace in NAMESPACES:
        api.add_namespace(namespace)
    return api


if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"))
