from http import HTTPStatus
from typing import List, Dict, Any, Optional, Tuple

import psycopg2
from flask import make_response

from database_client.database_client import DatabaseClient
from utilities.common import convert_dates_to_strings
from psycopg2.extensions import connection as PgConnection


ARCHIVES_GET_COLUMNS = [
    "id",
    "source_url",
    "update_frequency",
    "last_cached",
]


def archives_get_query(
    db_client: DatabaseClient,
) -> List[Dict[str, Any]]:
    """
    Processes the archives get results, either from the database and converts dates to strings.

    :param db_client: The database client object.
    :return: A list of dictionaries with the query results after processing and date conversion.
    """
    results = db_client.get_data_sources_to_archive()
    archives_combined_results = [
        dict(zip(ARCHIVES_GET_COLUMNS, result)) for result in results
    ]
    archives_combined_results_clean = []
    for item in archives_combined_results:
        archives_combined_results_clean.append(convert_dates_to_strings(item))

    return archives_combined_results_clean


def update_archives_data(
    db_client: DatabaseClient,
    data_id: str,
    last_cached: str,
    broken_as_of: str,
):
    """
    Processes a request to update the data source

    :param db_client: The database client
    :param data_id:
    :param last_cached:
    :param broken_as_of:
    :return: A dictionary containing a message about the update operation
    """
    if broken_as_of:
        db_client.update_url_status_to_broken(data_id, broken_as_of, last_cached)
    
    db_client.update_last_cached(data_id, last_cached)

    return make_response({"status": "success"}, HTTPStatus.OK)
