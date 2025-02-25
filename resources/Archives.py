from flask import Response, request
from flask_restx import fields

from middleware.access_logic import (
    API_OR_JWT_AUTH_INFO,
    AccessInfoPrimary,
    WRITE_ONLY_AUTH_INFO,
    ARCHIVE_WRITE_AUTH_INFO,
)
from middleware.decorators import api_key_required, permissions_required, endpoint_info
from middleware.primary_resource_logic.archives_queries import (
    archives_get_query,
    update_archives_data,
)

import json
from typing import Any

from middleware.enums import PermissionsEnum
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import (
    ResponseInfo,
)
from utilities.namespace import create_namespace
from resources.PsycopgResource import PsycopgResource

namespace_archives = create_namespace()


@namespace_archives.route("/archives")
class Archives(PsycopgResource):
    """
    A resource for managing archive data, allowing retrieval and update of archived data sources.
    """

    @endpoint_info(
        namespace=namespace_archives,
        auth_info=API_OR_JWT_AUTH_INFO,
        schema_config=SchemaConfigs.ARCHIVES_GET,
        response_info=ResponseInfo(
            success_message="Returns a list of archived data sources.",
        ),
        description="Retrieves archived data sources from the database.",
    )
    def get(self, access_info: AccessInfoPrimary) -> Any:
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

    @endpoint_info(
        namespace=namespace_archives,
        auth_info=ARCHIVE_WRITE_AUTH_INFO,
        schema_config=SchemaConfigs.ARCHIVES_PUT,
        response_info=ResponseInfo(
            success_message="Successfully updated the archive data.",
        ),
        description="""
        Updates the archive data based on the provided JSON payload.
        Note that, for this endpoint only, the schema must be provided first as a json string,
        rather than as a typical JSON object.
        This will be changed in a later update to conform to the standard JSON schema.
        """,
    )
    def put(self, access_info: AccessInfoPrimary) -> Response:
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
        return self.run_endpoint(
            update_archives_data,
            data_id=id,
            last_cached=last_cached,
            broken_as_of=broken_as_of,
        )
