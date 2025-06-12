import os
from datetime import timedelta, date, datetime

from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from jwt import DecodeError, ExpiredSignatureError

from middleware.scheduled_tasks.manager import SchedulerManager
from middleware.security.jwt.core import SimpleJWT
from middleware.scheduled_tasks.check_database_health import check_database_health
from middleware.util.env import get_env_variable
from endpoints.instantiations.admin import namespace_admin
from endpoints.instantiations.batch import namespace_bulk
from endpoints.instantiations.callback import namespace_auth
from endpoints.instantiations.contact import namespace_contact
from endpoints.instantiations.data_requests import namespace_data_requests
from endpoints.instantiations.github_data_requests import namespace_github
from endpoints.instantiations.link_to_github import namespace_link_to_github
from endpoints.instantiations.locations import namespace_locations
from endpoints.instantiations.login_with_github import namespace_login_with_github
from endpoints.instantiations.map import namespace_map
from endpoints.instantiations.match import namespace_match
from endpoints.instantiations.metadata import namespace_metadata
from endpoints.instantiations.metrics import namespace_metrics
from endpoints.instantiations.notifications import namespace_notifications
from endpoints.instantiations.oauth import namespace_oauth
from endpoints.instantiations.permissions import namespace_permissions
from endpoints.instantiations.proposals import namespace_proposals
from endpoints.instantiations.search import namespace_search
from endpoints.instantiations.signup import namespace_signup
from endpoints.instantiations.source_collector import namespace_source_collector
from endpoints.instantiations.typeahead_suggestions import (
    namespace_typeahead_suggestions,
)
from flask_restx import Api

from config import config, oauth, limiter, jwt
from db.helpers_.psycopg import initialize_psycopg_connection
from endpoints.instantiations.agencies import namespace_agencies
from endpoints.instantiations.api_key import namespace_api_key
from endpoints.instantiations.archives import namespace_archives
from endpoints.instantiations.data_sources import namespace_data_source
from endpoints.instantiations.login import namespace_login
from endpoints.instantiations.refresh_session import namespace_refresh_session
from endpoints.instantiations.request_reset_password import (
    namespace_request_reset_password,
)
from endpoints.instantiations.reset_password import namespace_reset_password
from endpoints.instantiations.reset_token_validation import (
    namespace_reset_token_validation,
)
from endpoints.instantiations.unique_url_checker import namespace_url_checker
from endpoints.instantiations.create_test_user_with_elevated_permissions import (
    namespace_create_test_user,
)
from endpoints.instantiations.user_profile import namespace_user

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
    namespace_proposals,
    namespace_source_collector,
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
            try:
                my_jwt = SimpleJWT.decode(token)
                environ["HTTP_X_USER_ID"] = my_jwt.other_claims["user_id"]
                return
            except (KeyError, DecodeError, ExpiredSignatureError):
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

    current_time = datetime.now()

    # Initialize and start the scheduler
    scheduler = SchedulerManager(app)
    scheduler.add_job(
        job_id="database_health_check",
        func=check_database_health,
        interval=IntervalTrigger(
            start_date=current_time + timedelta(minutes=3), minutes=60
        ),
    )

    scheduler.add_materialized_view_scheduled_job("typeahead_locations", 1)
    scheduler.add_materialized_view_scheduled_job("typeahead_agencies", 2)
    scheduler.add_materialized_view_scheduled_job("unique_urls", 3)
    scheduler.add_materialized_view_scheduled_job("map_states", 4)
    scheduler.add_materialized_view_scheduled_job("map_counties", 5)
    scheduler.add_materialized_view_scheduled_job("map_localities", 6)
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
