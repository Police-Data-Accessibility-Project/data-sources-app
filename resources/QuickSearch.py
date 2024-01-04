from flask_restful import Resource
from middleware.security import api_required
from middleware.quick_search_query import quick_search_query
import requests
import json
import os


class QuickSearch(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    # api_required decorator requires the request"s header to include an "Authorization" key with the value formatted as "Bearer [api_key]"
    # A user can get an API key by signing up and logging in (see User.py)
    @api_required
    def get(self, search, location):
        try:
            data_sources = quick_search_query(
                self.psycopg2_connection, search, location
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
                + f"Search term: {search}\n"
                + f"Location: {location}"
            }
            requests.post(
                webhook_url,
                data=json.dumps(message),
                headers={"Content-Type": "application/json"},
            )

            return {"count": 0, "message": user_message}, 500
