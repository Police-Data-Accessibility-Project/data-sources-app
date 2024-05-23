from flask import request
import os
import sys
import json

from middleware.token_management import insert_new_access_token
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from app import app

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")


class BaseEndpointHandler:
    def __init__(self, app, token):
        self.app = app
        self.token = token

    def send_request_with_token(self, path, arg1=None, arg2=None):
        path = path.format(arg1, arg2) if arg1 or arg2 else path
        with self.app.test_client() as client:
            response = client.get(
                path,
                headers={"Authorization": f"Bearer {self.token}"},
            )
        return json.loads(response.data), response.status_code


class QuickSearchHandler(BaseEndpointHandler):
    def get(self, arg1, arg2):
        return self.send_request_with_token("/quick-search/{}/{}/", arg1, arg2)


class DataSourcesHandler(BaseEndpointHandler):
    def get(self, _1, _2):
        return self.send_request_with_token("/data-sources")


class DataSourcesByIdHandler(BaseEndpointHandler):
    def get(self, arg1, _2):
        return self.send_request_with_token("/data-sources-by-id/{}", arg1)


class DataSourcesMapHandler(BaseEndpointHandler):
    def get(self, _1, _2):
        return self.send_request_with_token("/data-sources-map")


class SearchTokens(PsycopgResource):
    """
    A resource that provides various search functionalities based on the specified endpoint.
    It supports quick search, data source retrieval by ID, and listing all data sources.

    The search tokens endpoint generates an API token valid for 5 minutes and
     forwards the search parameters to the Quick Search endpoint.
    This endpoint is meant for use by the front end only.
    """

    endpoint_handlers = {
        "quick-search": QuickSearchHandler,
        "data-sources": DataSourcesHandler,
        "data-sources-by-id": DataSourcesByIdHandler,
        "data-sources-map": DataSourcesMapHandler,
    }

    @handle_exceptions
    def get(self):
        url_params = request.args
        endpoint = url_params.get("endpoint")
        arg1 = url_params.get("arg1")
        arg2 = url_params.get("arg2")

        cursor = self.psycopg2_connection.cursor()
        token = insert_new_access_token(cursor)

        self.psycopg2_connection.commit()

        handler = self.endpoint_handlers.get(endpoint)

        if handler is None:
            return {"message": "Unknown endpoint"}, 500
        resp_handler = handler(app, token)
        return resp_handler.get(arg1, arg2)
