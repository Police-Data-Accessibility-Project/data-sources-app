from flask import request, Response
from flask_restx import fields

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



data_sources_outer_model = namespace_data_source.model(
    "DataSourcesOuter",
    {
        "count": fields.Integer(required=True, description="The count of data objects"),
        "data": fields.List(
            fields.Wildcard(fields.String),
            required=True,
            description="The list of data objects",
        )
    },
)



@namespace_data_source.route("/data-sources-by-id/<data_source_id>")
@namespace_data_source.param(
    name="data_source_id",
    description="The unique identifier of the data source.",
    _in="path",
)
@namespace_data_source.doc(
    security="apikey",
)
class DataSourceById(PsycopgResource):
    """
    A resource for managing data source entities by their unique identifier.
    Provides methods for retrieving and updating data source details.
    """

    @handle_exceptions
    @api_required
    @namespace_data_source.response(200, "Success", data_sources_outer_model)
    @namespace_data_source.response(400, "Missing or bad API key")
    @namespace_data_source.response(403, "Forbidden Invalid API key")
    @namespace_data_source.response(404, "Data source not found")
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.doc(
        description="Get details of a specific data source by its ID.",
        security="apikey",
    )
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
    @namespace_data_source.expect(data_sources_outer_model)
    @namespace_data_source.doc(
        description="Update details of a specific data source by its ID.",
        security="apikey",
    )
    @namespace_data_source.response(200, "Successful operation")
    @namespace_data_source.response(400, "Missing or bad API key")
    @namespace_data_source.response(403, "Forbidden Invalid API key")
    @namespace_data_source.response(500, "Internal server error")
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
    @namespace_data_source.response(200, "Success", data_sources_outer_model)
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Retrieves all data sources.",
        security="apikey",
    )
    def get(self) -> Response:
        """
        Retrieves all data sources. The data sources endpoint returns all approved rows in the corresponding Data
        Sources database table.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        with self.setup_database_client() as db_client:
            return get_approved_data_sources_wrapper(db_client)

    @handle_exceptions
    @api_required
    @namespace_data_source.expect(data_sources_outer_model)
    @namespace_data_source.response(200, "Successful operation")
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Adds a new data source.",
        security="apikey",
    )
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


    @namespace_data_source.response(200, "Success", data_sources_outer_model)
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Retrieves all data sources needing identification.",
        security="apikey",
    )
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
    @namespace_data_source.response(200, "Success", data_sources_outer_model)
    @namespace_data_source.response(500, "Internal server error")
    @namespace_data_source.response(400, "Bad request; missing or bad API key")
    @namespace_data_source.response(403, "Forbidden; invalid API key")
    @namespace_data_source.doc(
        description="Retrieves location-relevant columns for data sources.",
        security="apikey"
    )
    def get(self) -> Response:
        """
        Retrieves location relevant columns for data sources.

        Returns:
        - A dictionary containing the count of data sources and their details.
        """
        with self.setup_database_client() as db_client:
            return get_data_sources_for_map_wrapper(db_client)
