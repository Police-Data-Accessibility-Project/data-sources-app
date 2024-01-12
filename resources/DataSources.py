from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from middleware.data_source_queries import data_source_by_id_query, data_sources_query
import json
from datetime import datetime
from utilities.common import convert_dates_to_strings
import uuid


class DataSourceById(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self, data_source_id):
        try:
            data_source_details = data_source_by_id_query(
                self.psycopg2_connection, data_source_id
            )
            if data_source_details:
                return data_source_details

            else:
                return "Data source not found.", 404

        except Exception as e:
            print(str(e))
            return "There has been an error pulling data!"

    @api_required
    def put(self, data_source_id):
        try:
            data = request.get_json()

            restricted_columns = [
                "rejection_note",
                "data_source_request",
                "approval_status",
                "airtable_uid",
                "airtable_source_last_modified",
            ]

            data_to_update = ""

            for key, value in data.items():
                if key not in restricted_columns:
                    if type(value) == str:
                        data_to_update += f"{key} = '{value}', "
                    else:
                        data_to_update += f"{key} = {value}, "

            data_to_update = data_to_update[:-2]

            cursor = self.psycopg2_connection.cursor()

            sql_query = f"""
            UPDATE data_sources 
            SET {data_to_update}
            WHERE airtable_uid = '{data_source_id}'
            """

            print(sql_query)

            cursor.execute(sql_query)
            self.psycopg2_connection.commit()
            return {"status": "success"}

        except Exception as e:
            print(str(e))
            return "There has been an error updating the data source", 400


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

    @api_required
    def post(self):
        try:
            data = request.get_json()
            cursor = self.psycopg2_connection.cursor()

            restricted_columns = [
                "rejection_note",
                "data_source_request",
                "approval_status",
                "airtable_uid",
                "airtable_source_last_modified",
            ]

            column_names = ""
            column_values = ""
            for key, value in data.items():
                if key not in restricted_columns:
                    column_names += f"{key}, "
                    if type(value) == str:
                        column_values += f"'{value}', "
                    else:
                        column_values += f"{value}, "

            now = datetime.now().strftime("%Y-%m-%d")
            airtable_uid = str(uuid.uuid4())

            column_names += (
                "approval_status, url_status, data_source_created, airtable_uid"
            )
            column_values += f"False, '[\"ok\"]', '{now}', '{airtable_uid}'"

            sql_query = f"INSERT INTO data_sources ({column_names}) VALUES ({column_values}) RETURNING *"

            cursor.execute(sql_query)
            self.psycopg2_connection.commit()

            return True

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return False
