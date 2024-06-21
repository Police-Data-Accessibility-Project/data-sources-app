from middleware.access_token_logic import insert_access_token
from flask import request, Response
import os
import sys

from middleware.search_tokens_logic import perform_endpoint_logic
from resources.PsycopgResource import PsycopgResource, handle_exceptions

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")


class SearchTokens(PsycopgResource):
    """
    A resource that provides various search functionalities based on the specified endpoint.
    It supports quick search, data source retrieval by ID, and listing all data sources.
    """

    @handle_exceptions
    def get(self) -> Response:
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

        cursor = self.psycopg2_connection.cursor()
        insert_access_token(cursor)
        response = perform_endpoint_logic(arg1, arg2, endpoint, cursor)
        self.psycopg2_connection.commit()
        return response
