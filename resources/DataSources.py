from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from middleware.data_source_queries import data_source_by_id_query, data_sources_query
import json


class DataSourceById(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self, data_source_id):
        try:
            data_source_details = data_source_by_id_query(
                data_source_id=data_source_id, conn=self.psycopg2_connection
            )
            if data_source_details:
                return data_source_details

            else:
                return "Data source not found.", 404

        except Exception as e:
            print(str(e))
            return "There has been an error pulling data!"


class DataSources(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self):
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
