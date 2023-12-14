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
            data_source_details = data_source_by_id_query(self.psycopg2_connection, data_source_id)
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
            json_data = request.get_json()
            data = json.loads(json_data)

            data_to_update = ""

            for key, value in data.items():
                data_to_update += f"{key} = {value}"

            cursor = self.psycopg2_connection.cursor()
            sql_query = """
            UPDATE data_sources 
            SET %s
            WHERE airtable_uid = %s
            """
            cursor.execute(sql_query, data_to_update, data["id"])
            self.psycopg2_connection.commit()
            return {"status": "success"}

        except Exception as e:
            print(str(e))
            return "There has been an error updating the data source"

    
class DataSources(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required 
    def get(self):
        try:
            data_source_matches = data_sources_query(self.psycopg2_connection)

            data_sources = {
                "count": len(data_source_matches),
                "data": data_source_matches
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

            column_names = ", ".join(data.keys())
            column_values = ", ".join(data.values())

            sql_query = f"INSERT INTO data_sources ({column_names}) VALUES ({column_values}) RETURNING *"
            print(sql_query)

            cursor.execute(sql_query)
            self.psycopg2_connection.commit()

            return True
        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return False
    