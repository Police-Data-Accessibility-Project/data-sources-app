from middleware.search_query import SearchQueryEngine
from middleware.security import api_required
import requests
import json
import os
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from flask import request
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource


class Search(PsycopgResource):
    """
    Provides a resource for performing quick searches in the database for data sources
    based on user-provided search terms and location.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = SearchQueryEngine(connection=self.psycopg2_connection)

    # api_required decorator requires the request"s header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
    # A user can get an API key by signing up and logging in (see User.py)
    @api_required
    def get(self, coarse_record_types: str, location: str) -> Dict[str, Any]:
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
            data = request.get_json()
            test = data.get("test_flag")
        except:
            test = False

        if isinstance(coarse_record_types, str):
            course_record_types = [coarse_record_types]
        try:
            data_sources = self.engine.quick_search(course_record_types, location, test)

            if data_sources["count"] == 0:
                self.psycopg2_connection = initialize_psycopg2_connection()
                data_sources = self.engine.quick_search(course_record_types, location)

            if data_sources["count"] == 0:
                return {
                    "count": 0,
                    "message": "No results found. Please considering requesting a new data source.",
                }, 404

            return {
                "message": "Results for search successfully retrieved",
                "data": data_sources,
            }

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
                + f"Record Types: {course_record_types}\n"
                + f"Location: {location}"
            }
            requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
            )

            return {"count": 0, "message": user_message}, 500
