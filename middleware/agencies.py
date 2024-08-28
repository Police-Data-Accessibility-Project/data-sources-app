from http import HTTPStatus

from flask import Response, make_response

from database_client.database_client import DatabaseClient
from middleware.access_logic import AccessInfo
from middleware.dataclasses import MiddlewareParameters, EntryDataRequest
from middleware.enums import Relations
from middleware.get_by_id_logic import get_many, get_by_id, post_entry
from utilities.common import convert_dates_to_strings
from middleware.util import format_list_response


def get_agencies(db_client: DatabaseClient, access_info: AccessInfo, page: int) -> Response:
    """
    Retrieves a paginated list of approved agencies from the database.

    :param db_client: The database client object.
    :param page: The page number of results to return.
    :return: A response object with the relevant agency information and status code.
    """
    return get_many(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agencies",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.get_agencies
        ),
        page=page
    )

def get_agency_by_id(db_client: DatabaseClient, access_info: AccessInfo, agency_id: str) -> Response:
    return get_by_id(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.get_agencies
        ),
        id=agency_id

    )

def create_agency(
    db_client: DatabaseClient,
    dto: EntryDataRequest,
    access_info: AccessInfo
) -> Response:
    return post_entry(
        middleware_parameters=MiddlewareParameters(
            db_client=db_client,
            access_info=access_info,
            entry_name="agency",
            relation=Relations.AGENCIES.value,
            db_client_method=DatabaseClient.create_agency
        ),
        entry=dto.entry_data
    )