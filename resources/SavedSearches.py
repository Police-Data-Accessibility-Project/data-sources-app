from flask_restful import Resource, reqparse
from flask import request

from middleware.saved_search_queries import (
    save_search,
    get_saved_searches,
    execute_search,
)
from middleware.security import api_required


class SavedSearches(Resource):
    def __init__(self, **kwargs):
        """
        Initializes the DataSourceById resource with a database connection.

        Parameters:
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def post(self, user_id: str):
        """
        Save a search query associated with the user
        and return a permanent id for the search url
        :param user_id:
        :return:
        """
        # `search_data` is expected as JSON body or form data
        parser = reqparse.RequestParser()
        parser.add_argument(
            "search_data",
            required=True,
            help="Search data is required",
            location="json",
        )
        args = parser.parse_args()
        permalink = save_search(user_id, args["search_data"])
        return {"message": "Search saved successfully", "data": permalink}, 201

    @api_required
    def get(self, user_id):
        """
        Retrieve saved searches for user up to limit
        :param user_id:
        :return:
        """
        limit = request.args.get("limit", default=10, type=int)
        # Logic to retrieve saved searches, using `user_id` and `limit`
        searches = get_saved_searches(user_id, limit)
        return {"count": len(searches), "data": searches}


class ExecuteSavedSearch(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self, search_id):
        """
        Execute a search from a saved search URL identified by search_id
        :param search_id: Unique identifier for the saved search to execute
        :return: Search results
        """
        # Assuming a function to execute the search
        search_results = execute_search(search_id)
        if search_results:
            return {"status": "success", "data": search_results}, 200
        else:
            return {
                "status": "error",
                "message": "No search found with provided ID",
            }, 404
