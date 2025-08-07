from flask import Response, make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.map.locations.queries.federal import GET_FEDERAL_QUERY


def get_data_for_map_wrapper(db_client: DatabaseClient) -> Response:
    results = {
        "locations": {
            "localities": db_client.get_map_localities(),
            "counties": db_client.get_map_counties(),
            "states": db_client.get_map_states(),
        },
        "sources": db_client.execute_raw_sql(GET_FEDERAL_QUERY)
    }
    return make_response(results)