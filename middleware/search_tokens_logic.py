import psycopg2.extensions
from flask import Response

from middleware.data_source_queries import get_approved_data_sources_wrapper, data_source_by_id_wrapper, \
    get_data_sources_for_map_wrapper
from middleware.quick_search_query import quick_search_query_wrapper


class UnknownEndpointError(Exception):
    def __init__(self, endpoint):
        self.message = f"Unknown endpoint: {endpoint}"
        super().__init__(self.message)


from enum import Enum

class Endpoint(Enum):
    QUICK_SEARCH = "quick-search"
    DATA_SOURCES = "data-sources"
    DATA_SOURCES_BY_ID = "data-sources-by-id"
    DATA_SOURCES_MAP = "data-sources-map"

def perform_endpoint_logic(
    arg1: str, arg2: str, endpoint_str: str, conn: psycopg2.extensions.connection
) -> Response:
    try:
        endpoint = Endpoint(endpoint_str)
    except ValueError:
        raise UnknownEndpointError(endpoint_str)

    if endpoint == Endpoint.QUICK_SEARCH:
        return quick_search_query_wrapper(arg1, arg2, conn)
    if endpoint == Endpoint.DATA_SOURCES:
        return get_approved_data_sources_wrapper(conn)
    if endpoint == Endpoint.DATA_SOURCES_BY_ID:
        return data_source_by_id_wrapper(arg1, conn)
    if endpoint == Endpoint.DATA_SOURCES_MAP:
        return get_data_sources_for_map_wrapper(conn)
