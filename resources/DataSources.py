
from flask import request, Response

from middleware.security import api_required
from middleware.data_source_queries import (
    get_approved_data_sources_wrapper,
    data_source_by_id_wrapper,
    get_data_sources_for_map_wrapper,
    add_new_data_source_wrapper,
    update_data_source_wrapper,
    needs_identification_data_sources_wrapper,
)
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_data_source = create_namespace()

@namespace_data_source.route("/data-sources-by-id/<data_source_id>")
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @handle_exceptions
    @api_required
    def get(self, data_source_id: str) -> Response:
        """
        Retrieves details of a specific data source by its ID.

        Parameters:
        - data_source_id (str): The unique identifier of the data source.

        Returns:
        - Tuple containing the response message with data source details if found, and the HTTP status code.
        """
        with self.setup_database_client() as db_client:
            return data_source_by_id_wrapper(data_source_id, db_client)

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
        with self.setup_database_client() as db_client:
            return update_data_source_wrapper(db_client, data, data_source_id)

@namespace_data_source.route("/data-sources")
class DataSources(PsycopgResource):
    """
    A resource for managing collections of data sources.
    Provides methods for retrieving all data sources and adding new ones.
    """

    @handle_exceptions
    @api_required
    def get(self) -> Response:
        """
        Retrieves all data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        with self.setup_database_client() as db_client:
            return get_approved_data_sources_wrapper(db_client)

    @handle_exceptions
    @api_required
    def post(self) -> Response:
        """
        Adds a new data source based on the provided JSON payload.

        Returns:
        - A dictionary containing a message about the addition operation.
        """
        data = request.get_json()
        with self.setup_database_client() as db_client:
            return add_new_data_source_wrapper(db_client, data)

@namespace_data_source.route("/data-sources-needs-identification")
class DataSourcesNeedsIdentification(PsycopgResource):

    @handle_exceptions
    @api_required
    def get(self):
        with self.setup_database_client() as db_client:
            return needs_identification_data_sources_wrapper(db_client)

@namespace_data_source.route("/data-sources-map")
class DataSourcesMap(PsycopgResource):
    """
    A resource for managing collections of data sources for mapping.
    Provides a method for retrieving all data sources.
    """

    @handle_exceptions
    @api_required
    def get(self) -> Response:
        """
        Retrieves location relevant columns for data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        with self.setup_database_client() as db_client:
            return get_data_sources_for_map_wrapper(db_client)
