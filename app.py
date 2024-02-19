from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from resources.User import User
from resources.Login import Login
from resources.ApiKey import ApiKey
from resources.RequestResetPassword import RequestResetPassword
from resources.ResetPassword import ResetPassword
from resources.QuickSearch import QuickSearch
from resources.DataSources import DataSources
from resources.DataSources import DataSourceById
from resources.Agencies import Agencies
from resources.Archives import Archives
from resources.SearchTokens import SearchTokens
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection

psycopg2_connection = initialize_psycopg2_connection()

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(
    User, "/user", resource_class_kwargs={"psycopg2_connection": psycopg2_connection}
)
api.add_resource(
    Login, "/login", resource_class_kwargs={"psycopg2_connection": psycopg2_connection}
)
api.add_resource(
    ApiKey,
    "/api_key",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    RequestResetPassword,
    "/request-reset-password",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    ResetPassword,
    "/reset-password/<token>",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    QuickSearch,
    "/quick-search/<search>/<location>",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    Archives,
    "/archives",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    DataSources,
    "/data-sources",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    DataSourceById,
    "/data-sources-by-id/<data_source_id>",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    Agencies,
    "/agencies/<page>",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)
api.add_resource(
    SearchTokens,
    "/search-tokens",
    resource_class_kwargs={"psycopg2_connection": psycopg2_connection},
)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
