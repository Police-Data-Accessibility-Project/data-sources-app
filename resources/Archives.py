from flask_jwt_extended import jwt_required
from flask_restx import fields

from middleware.decorators import api_key_required, permissions_required
from middleware.archives_queries import (
    archives_get_query,
    update_archives_data,
)
from flask_restful import request

import json
from typing import Dict, Any

from middleware.enums import PermissionsEnum
from resources.resource_helpers import add_api_key_header_arg, add_jwt_header_arg
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_archives = create_namespace()

archives_get_model = namespace_archives.model(
    "ArchivesResponse",
    {
        "id": fields.String(description="The ID of the data source"),
        "last_cached": fields.DateTime(description="The last date the data was cached"),
        "source_url": fields.String(description="The URL of the data source"),
        "update_frequency": fields.String(
            description="The archive update frequency of the data source"
        ),
    },
)

archives_post_model = namespace_archives.model(
    "ArchivesPost",
    {
        "id": fields.String(description="The ID of the data source", required=True),
        "last_cached": fields.DateTime(description="The last date the data was cached"),
        "broken_source_url_as_of": fields.Date(
            description="The date the source was marked as broken"
        ),
    },
)

archives_header_get_parser = namespace_archives.parser()
add_api_key_header_arg(archives_header_get_parser)

archives_header_post_parser = namespace_archives.parser()
add_jwt_header_arg(archives_header_post_parser)


@namespace_archives.route("/archives")
class Archives(PsycopgResource):
    """
    A resource for managing archive data, allowing retrieval and update of archived data sources.
    """

    @handle_exceptions
    @api_key_required
    @namespace_archives.response(
        200, "Success: Returns a list of archived data sources", archives_get_model
    )
    @namespace_archives.response(400, "Error: Bad request missing or bad API key")
    @namespace_archives.response(
        403, "Error: Unauthorized. Forbidden or an invalid API key"
    )
    @namespace_archives.doc(
        description="Retrieves archived data sources from the database.",
    )
    @namespace_archives.expect(archives_header_get_parser)
    def get(self) -> Any:
        """
        Retrieves archived data sources from the database.

        Uses an API-required middleware for security and a database connection to fetch archived data.

        Returns:
        - Any: The cleaned results of archives combined from the database query, or an error message if an exception occurs.
        """
        with self.setup_database_client() as db_client:
            archives_combined_results_clean = archives_get_query(
                db_client=db_client,
            )

        return archives_combined_results_clean

    @handle_exceptions
    @permissions_required(PermissionsEnum.DB_WRITE)
    @namespace_archives.doc(
        description="Updates the archive data based on the provided JSON payload.",
        responses={
            200: "Success: Returns a status message indicating success or an error message if an exception occurs.",
            400: "Error: Bad request missing or bad API key",
            403: "Error: Unauthorized. Forbidden or an invalid API key",
            500: "Error: Internal server error",
        },
    )
    @namespace_archives.expect(archives_header_post_parser, archives_post_model)
    def put(self) -> Dict[str, str]:
        """
        Updates the archive data based on the provided JSON payload.

        Expects a JSON payload with archive data source identifiers and updates them in the database. The put method
        on the archives endpoint updates the data source matching the passed id, updating the last_cached date if it
        alone is passed, or it and the broken_source_url_as_of field and the url_status to 'broken'.

        Returns:
            -   dict: A status message indicating success or an error message if an exception occurs.
        """
        json_data = request.get_json()
        data = json.loads(json_data)
        id = data["id"] if "id" in data else None
        last_cached = data["last_cached"] if "last_cached" in data else None
        broken_as_of = (
            data["broken_source_url_as_of"]
            if "broken_source_url_as_of" in data
            else None
        )

        with self.setup_database_client() as db_client:
            response = update_archives_data(db_client, id, last_cached, broken_as_of)

        return response
