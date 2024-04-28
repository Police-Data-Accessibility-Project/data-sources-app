from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from resources.DataRequest import DataRequest
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


def add_resource(api, resource, endpoint, **kwargs):
    api.add_resource(resource, endpoint, resource_class_kwargs=kwargs)


def create_app() -> Flask:
    psycopg2_connection = initialize_psycopg2_connection()

    app = Flask(__name__)
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
        (DataRequest, "/data-request")
    ]

    for resource, endpoint in resources:
        add_resource(api, resource, endpoint, psycopg2_connection=psycopg2_connection)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
