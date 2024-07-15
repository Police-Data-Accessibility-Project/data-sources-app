import os

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from resources.User import User
from resources.Login import Login
from resources.RefreshSession import RefreshSession
from resources.ApiKey import ApiKey
from resources.RequestResetPassword import RequestResetPassword
from resources.ResetPassword import ResetPassword
from resources.ResetTokenValidation import ResetTokenValidation
from resources.QuickSearch import QuickSearch
from resources.DataSources import (
    DataSources,
    DataSourcesNeedsIdentification,
    DataSourceById,
    DataSourcesMap,
)
from resources.Agencies import Agencies
from resources.Archives import Archives
from resources.SearchTokens import SearchTokens
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection

MY_PREFIX = '/api'

class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = MY_PREFIX
        environ['SCRIPT_NAME'] = script_name
        path_info = environ['PATH_INFO']
        if path_info.startswith(script_name):
            environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

def add_resource(api, resource, endpoint, **kwargs):
    api.add_resource(resource, endpoint, resource_class_kwargs=kwargs)


def create_app() -> Flask:
    psycopg2_connection = initialize_psycopg2_connection()
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    api = Api(app)
    CORS(app)

    resources = [
        (User, "/user"),
        (Login, "/login"),
        (RefreshSession, "/refresh-session"),
        (ApiKey, "/api_key"),
        (RequestResetPassword, "/request-reset-password"),
        (ResetPassword, "/reset-password"),
        (ResetTokenValidation, "/reset-token-validation"),
        (QuickSearch, "/quick-search/<search>/<location>"),
        (Archives, "/archives"),
        (DataSources, "/data-sources"),
        (DataSourcesMap, "/data-sources-map"),
        (DataSourcesNeedsIdentification, "/data-sources-needs-identification"),
        (DataSourceById, "/data-sources-by-id/<data_source_id>"),
        (Agencies, "/agencies/<page>"),
        (SearchTokens, "/search-tokens"),
    ]

    for resource, endpoint in resources:
        add_resource(api, resource, endpoint, psycopg2_connection=psycopg2_connection)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'))
