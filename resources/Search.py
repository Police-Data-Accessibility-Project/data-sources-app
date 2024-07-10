from flask import Response, request

from middleware.search_logic import search_wrapper
from middleware.security import api_required
from resources.PsycopgResource import PsycopgResource
from utilities.enums import RecordCategories


class Search(PsycopgResource):
    """
    Provides a resource for performing searches in the database for data sources
    based on user-provided search terms and location.
    """

    @api_required
    def get(self) -> Response:
        """
        Performs a search using the provided search terms and location. It attempts to find relevant
        data sources in the database. If no results are found initially, it re-initializes the database
        connection and tries again.

        Parameters:
        - search (str): The search term provided by the user.
        - location (str): The location provided by the user.

        Returns:
        - A dictionary containing a message about the search results and the data found, if any.
        """
        state = request.args.get("state")
        county = request.args.get("county")
        locality = request.args.get("locality")
        record_category_raw = request.args.get("record_category")
        if record_category_raw is not None:
            record_category = RecordCategories(record_category_raw)
        else:
            record_category = None

        with self.setup_database_client() as db_client:
            response = search_wrapper(
                db_client=db_client,
                record_category=record_category,
                state=state,
                county=county,
                locality=locality
            )
        return response
