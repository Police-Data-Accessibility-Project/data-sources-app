from middleware.quick_search_query import quick_search_query_wrapper
from middleware.data_source_queries import (
    data_source_by_id_query,
    get_data_sources_for_map,
    get_approved_data_sources,
    get_approved_data_sources_wrapper,
    data_source_by_id_wrapper,
    get_data_sources_for_map_wrapper,
)
from flask import request
import datetime
import uuid
import os
import sys
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")


def insert_access_token(cursor):
    token = uuid.uuid4().hex
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cursor.execute(
        f"insert into access_tokens (token, expiration_date) values (%s, %s)",
        (token, expiration),
    )


class SearchTokens(PsycopgResource):
    """
    A resource that provides various search functionalities based on the specified endpoint.
    It supports quick search, data source retrieval by ID, and listing all data sources.
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

        cursor = self.psycopg2_connection.cursor()
        insert_access_token(cursor)
        self.psycopg2_connection.commit()

        if endpoint == "quick-search":
            return quick_search_query_wrapper(arg1, arg2, self.psycopg2_connection)
        elif endpoint == "data-sources":
            return get_approved_data_sources_wrapper(self.psycopg2_connection)
        elif endpoint == "data-sources-by-id":
            return data_source_by_id_wrapper(arg1, self.psycopg2_connection)
        elif endpoint == "data-sources-map":
            return get_data_sources_for_map_wrapper(self.psycopg2_connection)
        else:
            return {"message": "Unknown endpoint"}, 500
