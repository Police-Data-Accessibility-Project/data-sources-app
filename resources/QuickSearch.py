from middleware.security import api_required
from middleware.quick_search_query import quick_search_query, SearchParameters
import requests
import json
import os
from flask import make_response, Response

from resources.PsycopgResource import PsycopgResource
from utilities.managed_cursor import managed_cursor


class QuickSearch(PsycopgResource):
    """
    Provides a resource for performing quick searches in the database for data sources
    based on user-provided search terms and location.
    """

    # api_required decorator requires the request"s header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
    # A user can get an API key by signing up and logging in (see User.py)
    @api_required
    def get(self, search: str, location: str) -> Response:
        """
        Performs a quick search using the provided search terms and location. It attempts to find relevant
        data sources in the database. If no results are found initially, it re-initializes the database
        connection and tries again.

        Parameters:
        - search (str): The search term provided by the user.
        - location (str): The location provided by the user.

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        try:

            with managed_cursor(self.psycopg2_connection) as cursor:
                data_sources = quick_search_query(
                    SearchParameters(search, location), cursor
                )

            if data_sources["count"] == 0:
                return make_response(
                    {
                        "count": 0,
                        "message": "No results found. Please considering requesting a new data source.",
                    },
                    200,
                )

            return make_response(
                {
                    "message": "Results for search successfully retrieved",
                    "data": data_sources,
                },
                200,
            )

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
                + f"Search term: {search}\n"
                + f"Location: {location}"
            }
            requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
            )

            return {"count": 0, "message": user_message}, 500
