from flask import Response, make_response

from db.client.core import DatabaseClient


def get_locations_for_map_wrapper(db_client: DatabaseClient) -> Response:
    return make_response(
        {
            "localities": db_client.get_map_localities(),
            "counties": db_client.get_map_counties(),
            "states": db_client.get_map_states(),
        }
    )
