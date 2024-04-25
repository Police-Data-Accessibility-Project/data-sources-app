from flask_restful import Resource, reqparse
from flask import request


class SavedSearches(Resource):
    def __init__(self, **kwargs):
        """
        Initializes the DataSourceById resource with a database connection.

        Parameters:
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def post(self, user_id: str):
        # `search_data` is expected as JSON body or form data
        parser = reqparse.RequestParser()
        parser.add_argument(
            "search_data",
            required=True,
            help="Search data is required",
            location="json",
        )
        args = parser.parse_args()
        permalink = save_search(user_id, args['search_data'])
        return {"message": "Search saved successfully", "data": permalink}, 201

    def get(self, user_id):
        # `limit` is a query parameter; it's optional, so we provide a default
        limit = request.args.get('limit', default=10, type=int)
        # Logic to retrieve saved searches, using `user_id` and `limit`
        searches = get_saved_searches(user_id, limit)
        return {"count": len(searches), "data": searches}
