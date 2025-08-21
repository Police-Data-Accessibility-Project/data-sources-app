from flask import Response, make_response

from db.client.core import DatabaseClient
from endpoints.instantiations.map.data_sources.format import zip_get_datas_sources_for_map_results
from middleware.common_response_formatting import format_list_response


def get_data_sources_for_map_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_data_sources_for_map()
    zipped_results = zip_get_datas_sources_for_map_results(raw_results)
    return make_response(
        format_list_response(
            data={"data": zipped_results},
        )
    )
