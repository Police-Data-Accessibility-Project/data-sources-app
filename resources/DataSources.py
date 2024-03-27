from flask_restful import Resource
from flask import request, jsonify
from middleware.security import api_required
from middleware.data_source_queries import data_source_by_id_query, data_sources_query
import json
from datetime import datetime

import uuid
from typing import Dict, Any, Tuple

class DataSourceById(Resource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """
    def __init__(self, **kwargs):
        """
        Initializes the DataSourceById resource with a database connection.

        Parameters:
        - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self, data_source_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Retrieves details of a specific data source by its ID.

        Parameters:
        - data_source_id (str): The unique identifier of the data source.

        Returns:
        - Tuple containing the response message with data source details if found, and the HTTP status code.
        """
        try:
            data_source_details = data_source_by_id_query(
                conn=self.psycopg2_connection, data_source_id=data_source_id
            )
            if data_source_details:
                return {
                    "message": "Successfully found data source",
                    "data": data_source_details,
                }

            else:
                return {"message": "Data source not found."}, 404

        except Exception as e:
            print(str(e))
            return {"message": "There has been an error pulling data!"}, 500

    @api_required
    def put(self, data_source_id: str) -> Dict[str, str]:
        """
        Updates a data source by its ID based on the provided JSON payload.

        Parameters:
        - data_source_id (str): The unique identifier of the data source to update.

        Returns:
        - A dictionary containing a message about the update operation.
        """
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

            cursor.execute(sql_query)
            self.psycopg2_connection.commit()
            return {"message": "Data source updated successfully."}

        except Exception as e:
            print(str(e))
            return {"message": "There has been an error updating the data source"}, 500


class DataSources(Resource):
    """
    A resource for managing collections of data sources.
    Provides methods for retrieving all data sources and adding new ones.
    """

    def __init__(self, **kwargs):
        """
                Initializes the DataSources resource with a database connection.

                Parameters:
                - kwargs (dict): Keyword arguments containing 'psycopg2_connection' for database connection.
        """
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self) -> Dict[str, Any]:
        """
        Retrieves all data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        try:
            data_source_matches = data_sources_query(
                self.psycopg2_connection, [], "approved"
            )

            data_sources = {
                "count": len(data_source_matches),
                "data": data_source_matches,
            }

            return data_sources

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": "There has been an error pulling data!"}, 500

    @api_required
    def post(self) -> Dict[str, str]:
        """
        Adds a new data source based on the provided JSON payload.

        Returns:
        - A dictionary containing a message about the addition operation.
        """
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

            return {"message": "Data source added successfully."}

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": "There has been an error adding the data source"}, 500


class DataSourcesNeedsIdentification(Resource):
    def __init__(self, **kwargs):
        self.psycopg2_connection = kwargs["psycopg2_connection"]

    @api_required
    def get(self):
        try:
            data_source_matches = data_sources_query(
                self.psycopg2_connection, [], "needs_identification"
            )

            data_sources = {
                "count": len(data_source_matches),
                "data": data_source_matches,
            }

            return data_sources

        except Exception as e:
            self.psycopg2_connection.rollback()
            print(str(e))
            return {"message": "There has been an error pulling data!"}, 500
