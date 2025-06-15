from flask import Response, request

from config import limiter
from endpoints.schema_config.instantiations.archives.get import (
    ArchivesGetEndpointSchemaConfig,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.security.auth.info.instantiations import (
    ARCHIVE_WRITE_AUTH_INFO,
    API_OR_JWT_AUTH_INFO,
)
from middleware.decorators.endpoint_info import endpoint_info
from middleware.primary_resource_logic.archives_queries import (
    archives_get_query,
    update_archives_data,
)

from typing import Any

from endpoints.schema_config.enums import SchemaConfigs
from endpoints._helpers.response_info import ResponseInfo
from utilities.namespace import create_namespace
from endpoints.psycopg_resource import PsycopgResource

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
        return self.run_endpoint(
            wrapper_function=archives_get_query,
            schema_populate_parameters=ArchivesGetEndpointSchemaConfig.get_schema_populate_parameters(),
        )

    @endpoint_info(
        namespace=namespace_archives,
        auth_info=ARCHIVE_WRITE_AUTH_INFO,
        schema_config=SchemaConfigs.ARCHIVES_PUT,
        response_info=ResponseInfo(
            success_message="Successfully updated the archive data.",
        ),
        description="""
        Updates the archive data based on the provided JSON payload.
        """,
    )
    @limiter.limit("25/minute;1000/hour")
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
        id = json_data["id"] if "id" in json_data else None
        last_cached = json_data["last_cached"] if "last_cached" in json_data else None
        broken_as_of = (
            json_data["broken_source_url_as_of"]
            if "broken_source_url_as_of" in json_data
            else None
        )
        return self.run_endpoint(
            update_archives_data,
            data_id=id,
            last_cached=last_cached,
            broken_as_of=broken_as_of,
        )
