from middleware.quick_search_query import quick_search_query
from middleware.data_source_queries import data_source_by_id_query, data_sources_query
from flask import request, jsonify
from flask_restful import Resource
import datetime
import uuid
import os
import requests
import sys
import json

sys.path.append("..")

BASE_URL = os.getenv("VITE_VUE_APP_BASE_URL")


class SearchTokens(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    def get(self):
        try:
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
            # cursor.execute(f"insert into access_tokens (token, expiration_date) values (%s, %s)", (token, expiration))
            # self.psycopg2_connection.commit()

            if endpoint == "quick-search":
                try:
                    data_sources = quick_search_query(
                        arg1, arg2, [], self.psycopg2_connection
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
                    return "There has been an error pulling data!"

            elif endpoint == "data-sources-by-id":
                try:
                    data_source_details = data_source_by_id_query(
                        arg1, [], self.psycopg2_connection
                    )
                    if data_source_details:
                        return data_source_details

                    else:
                        return "Data source not found.", 404

                except Exception as e:
                    print(str(e))
                    return "There has been an error pulling data!"

            else:
                return {"error": "Unknown endpoint"}, 500

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": e}, 500
