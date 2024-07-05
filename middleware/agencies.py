from http import HTTPStatus

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from utilities.common import convert_dates_to_strings

def get_agencies(db_client: DatabaseClient, page: int) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    agencies_matches = get_agencies_matches(db_client, page)
    agencies = {"count": len(agencies_matches), "data": agencies_matches}
    return make_response(agencies, HTTPStatus.OK)


def get_agencies_matches(db_client: DatabaseClient, page: int):
    """
    Retrieves a paginated list of approved agencies from the database.
    Args:
        db_client (DatabaseClient): The database client object.
        page (int): The page number of results to return.
    Returns:
        list: A list of dictionaries containing the relevant agency information.
    """
    results = db_client.get_agencies_from_page(page)
    return process_results(results)


def process_results(results: list[dict]) -> list[dict]:
    """
    Processes the results by converting dates in each dictionary to strings.
    Args:
        results (list[dict]): A list of dictionaries containing the results.
    Returns:
        list[dict]: The processed list of dictionaries with converted dates.
    """
    return [convert_dates_to_strings(dict(result)) for result in results]


