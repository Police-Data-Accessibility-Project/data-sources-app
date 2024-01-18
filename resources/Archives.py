from middleware.security import api_required
from middleware.archives_queries import archives_get_query, archives_put_query
from flask_restful import Resource, request

import json


class Archives(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self):
        try:
            archives_combined_results_clean = archives_get_query(
                test_query_results=[], conn=self.psycopg2_connection
            )

            return archives_combined_results_clean

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return "There has been an error pulling data!"

    @api_required
    def put(self):
        try:
            json_data = request.get_json()
            data = json.loads(json_data)
            id = data["id"] if "id" in data else None
            broken_as_of = (
                data["broken_source_url_as_of"]
                if "broken_source_url_as_of" in data
                else None
            )
            last_cached = data["last_cached"] if "last_cached" in data else None

            archives_put_query(
                id=id,
                broken_as_of=broken_as_of,
                last_cached=last_cached,
                conn=self.psycopg2_connection,
            )

            return {"status": "success"}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"error": str(e)}
