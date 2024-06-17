from middleware.security import api_required
from middleware.archives_queries import (
    archives_get_query,
    archives_put_broken_as_of_results,
    archives_put_last_cached_results,
)
from flask_restful import request

import json
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource, handle_exceptions


class Archives(PsycopgResource):
    """
    A resource for managing archive data, allowing retrieval and update of archived data sources.
    """

    @handle_exceptions
    @api_required
    def get(self) -> Any:
        """
        Retrieves archived data sources from the database.

        Uses an API-required middleware for security and a database connection to fetch archived data.

        Returns:
        - Any: The cleaned results of archives combined from the database query, or an error message if an exception occurs.
        """
        archives_combined_results_clean = archives_get_query(
            conn=self.psycopg2_connection
        )

        return archives_combined_results_clean

    @handle_exceptions
    @api_required
    def put(self) -> Dict[str, str]:
        """
        Updates the archive data based on the provided JSON payload.

        Expects a JSON payload with archive data source identifiers and updates them in the database.

        Returns:
        - dict: A status message indicating success or an error message if an exception occurs.
        """
        json_data = request.get_json()
        data = json.loads(json_data)
        id = data["id"] if "id" in data else None
        last_cached = data["last_cached"] if "last_cached" in data else None

        if "broken_source_url_as_of" in data:
            archives_put_broken_as_of_results(
                id=id,
                broken_as_of=data["broken_source_url_as_of"],
                last_cached=last_cached,
                conn=self.psycopg2_connection,
            )
        else:
            archives_put_last_cached_results(id, last_cached, self.psycopg2_connection)

        self.psycopg2_connection.commit()

        return {"status": "success"}
