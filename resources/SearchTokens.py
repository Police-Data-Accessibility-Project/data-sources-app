from flask import request
import os
import sys
import json
from typing import Dict, Any

from middleware.token_management import insert_new_access_token
from resources.PsycopgResource import PsycopgResource, handle_exceptions
from app import app

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")


class SearchTokens(PsycopgResource):
    """
    A resource that provides various search functionalities based on the specified endpoint.
    It supports quick search, data source retrieval by ID, and listing all data sources.

    The search tokens endpoint generates an API token valid for 5 minutes and
     forwards the search parameters to the Quick Search endpoint.
    This endpoint is meant for use by the front end only.
    """

    @handle_exceptions
    def get(self) -> Dict[str, Any]:
        """
        Handles GET requests by performing a search operation based on the specified endpoint and arguments.

        The function supports the following endpoints:
        - quick-search: Performs a quick search with specified search terms and location.
        - data-sources: Retrieves a list of all data sources.
        - data-sources-by-id: Retrieves details of a data source by its ID.
        - data-sources-map: Retrieves data sources for the map.

        Returns:
        - A dictionary with the search results or an error message.
        """
        url_params = request.args
        endpoint = url_params.get("endpoint")
        arg1 = url_params.get("arg1")
        arg2 = url_params.get("arg2")
        print(endpoint, arg1, arg2)

        cursor = self.psycopg2_connection.cursor()
        token = insert_new_access_token(cursor)
        self.psycopg2_connection.commit()

        if endpoint == "quick-search":
            with app.test_client() as client:
                response = client.get(
                    f"/quick-search/{arg1}/{arg2}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                return json.loads(response.data)

        if endpoint == "data-sources":
            with app.test_client() as client:
                response = client.get(
                    "/data-sources",
                    headers={"Authorization": f"Bearer {token}"},
                )
                return json.loads(response.data)

        if endpoint == "data-sources-by-id":
            with app.test_client() as client:
                response = client.get(
                    f"/data-sources-by-id/{arg1}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                return json.loads(response.data)
        if endpoint == "data-sources-map":
            with app.test_client() as client:
                response = client.get(
                    "/data-sources-map",
                    headers={"Authorization": f"Bearer {token}"},
                )
                return json.loads(response.data)
        return {"message": "Unknown endpoint"}, 500
