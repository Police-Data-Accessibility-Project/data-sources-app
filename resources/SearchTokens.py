from middleware.quick_search_query import quick_search_query
from middleware.data_source_queries import (
    data_source_by_id_query,
)
from flask import request
import datetime
import uuid
import os
import requests
import sys
import json
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_API_BASE_URL")


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
        print(endpoint, arg1, arg2)
        data_sources = {"count": 0, "data": []}
        if type(self.psycopg2_connection) == dict:
            return data_sources

        cursor = self.psycopg2_connection.cursor()
        token = uuid.uuid4().hex
        expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
        cursor.execute(
            f"insert into access_tokens (token, expiration_date) values (%s, %s)",
            (token, expiration),
        )
        self.psycopg2_connection.commit()

        if endpoint == "quick-search":
            try:
                data = request.get_json()
                test = data.get("test_flag")
            except:
                test = False
            try:
                data_sources = quick_search_query(
                    arg1, arg2, [], self.psycopg2_connection, test
                )

                return data_sources

            except Exception as e:
                self.psycopg2_connection.rollback()
                print(str(e))
                webhook_url = os.getenv("WEBHOOK_URL")
                user_message = "There was an error during the search operation"
                message = {
                    "content": user_message
                    + ": "
                    + str(e)
                    + "\n"
                    + f"Search term: {arg1}\n"
                    + f"Location: {arg2}"
                }
                requests.post(
                    webhook_url,
                    data=json.dumps(message),
                    headers={"Content-Type": "application/json"},
                )

                return {"count": 0, "message": user_message}, 500

        elif endpoint == "data-sources":
            try:
                data_source_matches = data_sources_query(self.psycopg2_connection)

                data_sources = {
                    "count": len(data_source_matches),
                    "data": data_source_matches,
                }

                return data_sources

            except Exception as e:
                self.psycopg2_connection.rollback()
                print(str(e))
                return {"message": "There has been an error pulling data!"}, 500

        elif endpoint == "data-sources-by-id":
            try:
                data_source_details = data_source_by_id_query(
                    arg1, [], self.psycopg2_connection
                )
                if data_source_details:
                    return data_source_details

                else:
                    return {"message": "Data source not found."}, 404

            except Exception as e:
                print(str(e))
                return {"message": "There has been an error pulling data!"}, 500

        elif endpoint == "data-sources-map":
            try:
                data_source_details = data_sources_query(
                    self.psycopg2_connection, [], "approved", True
                )
                if data_source_details:
                    data_sources = {
                        "count": len(data_source_details),
                        "data": data_source_details,
                    }
                    return data_sources

                else:
                    return {"message": "There has been an error pulling data!"}, 500

            except Exception as e:
                print(str(e))
                return {"message": "There has been an error pulling data!"}, 500
        else:
            return {"message": "Unknown endpoint"}, 500
