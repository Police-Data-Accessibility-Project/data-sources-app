from flask import request, Response
from middleware.security import api_required
from middleware.data_source_queries import (
    needs_identification_data_sources,
    get_approved_data_sources_wrapper,
    data_source_by_id_wrapper,
    get_data_sources_for_map_wrapper,
    update_data_source,
    get_restricted_columns,
    add_new_data_source,
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
        return data_source_by_id_wrapper(data_source_id, self.psycopg2_connection)

    @handle_exceptions
    @api_required
    def put(self, data_source_id: str) -> Response:
        """
        Updates a data source by its ID based on the provided JSON payload.

        Parameters:
        - data_source_id (str): The unique identifier of the data source to update.

        Returns:
        - A dictionary containing a message about the update operation.
        """
        data = request.get_json()
        with self.psycopg2_connection.cursor() as cursor:
            result = update_data_source(cursor, data, data_source_id)
            self.psycopg2_connection.commit()

        return result


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
        return get_approved_data_sources_wrapper(self.psycopg2_connection)

    @handle_exceptions
    @api_required
    def post(self) -> Response:
        """
        Adds a new data source based on the provided JSON payload.

        Returns:
        - A dictionary containing a message about the addition operation.
        """
        data = request.get_json()
        with self.psycopg2_connection.cursor() as cursor:
            result = add_new_data_source(cursor, data)
            self.psycopg2_connection.commit()

        return result


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
        return get_data_sources_for_map_wrapper(self.psycopg2_connection)
