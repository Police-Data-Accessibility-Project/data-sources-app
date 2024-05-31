from flask import request
from middleware.security import api_required
from middleware.data_source_queries import (
    data_source_by_id_query,
    get_data_sources_for_map,
    get_approved_data_sources,
    needs_identification_data_sources,
)
from datetime import datetime

import uuid
from typing import Dict, Any, Tuple

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @handle_exceptions
    @api_required
    def get(self, data_source_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Retrieves details of a specific data source by its ID.

        Parameters:
        - data_source_id (str): The unique identifier of the data source.

        Returns:
        - Tuple containing the response message with data source details if found, and the HTTP status code.
        """
        data_source_details = data_source_by_id_query(
            conn=self.psycopg2_connection, data_source_id=data_source_id
        )
        if data_source_details:
            return {
                "message": "Successfully found data source",
                "data": data_source_details,
            }

        else:
            return {"message": "Data source not found."}, 200

    @handle_exceptions
    @api_required
    def put(self, data_source_id: str) -> Dict[str, str]:
        """
        Updates a data source by its ID based on the provided JSON payload.

        Parameters:
        - data_source_id (str): The unique identifier of the data source to update.

        Returns:
        - A dictionary containing a message about the update operation.
        """
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


class DataSources(PsycopgResource):
    """
    A resource for managing collections of data sources.
    Provides methods for retrieving all data sources and adding new ones.
    """

    @handle_exceptions
    @api_required
    def get(self) -> Dict[str, Any]:
        """
        Retrieves all data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        data_source_matches = get_approved_data_sources(self.psycopg2_connection)

        data_sources = {
            "count": len(data_source_matches),
            "data": data_source_matches,
        }

        return data_sources

    @handle_exceptions
    @api_required
    def post(self) -> Dict[str, str]:
        """
        Adds a new data source based on the provided JSON payload.

        Returns:
        - A dictionary containing a message about the addition operation.
        """
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

        column_names += "approval_status, url_status, data_source_created, airtable_uid"
        column_values += f"False, '[\"ok\"]', '{now}', '{airtable_uid}'"

        sql_query = f"INSERT INTO data_sources ({column_names}) VALUES ({column_values}) RETURNING *"

        cursor.execute(sql_query)
        self.psycopg2_connection.commit()

        return {"message": "Data source added successfully."}


class DataSourcesNeedsIdentification(PsycopgResource):

    @handle_exceptions
    @api_required
    def get(self):
        data_source_matches = needs_identification_data_sources(
            self.psycopg2_connection
        )

        data_sources = {
            "count": len(data_source_matches),
            "data": data_source_matches,
        }

        return data_sources


class DataSourcesMap(PsycopgResource):
    """
    A resource for managing collections of data sources for mapping.
    Provides a method for retrieving all data sources.
    """

    @handle_exceptions
    @api_required
    def get(self) -> Dict[str, Any]:
        """
        Retrieves location relevant columns for data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        data_source_matches = get_data_sources_for_map(self.psycopg2_connection)

        data_sources = {
            "count": len(data_source_matches),
            "data": data_source_matches,
        }

        return data_sources
