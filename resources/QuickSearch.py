from flask import Response

from middleware.security import api_required
from middleware.quick_search_query import quick_search_query_wrapper

from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource


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
        return quick_search_query_wrapper(
            search, location, self.psycopg2_connection.cursor()
        )
