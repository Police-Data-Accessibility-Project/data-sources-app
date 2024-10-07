"""Integration tests for /data-sources-map endpoint"""

from http import HTTPStatus
import psycopg
from tests.conftest import connection_with_test_data, flask_client_with_db
from tests.helper_scripts.helper_functions import (
    create_test_user_api,
    create_api_key,
    create_test_user_setup,
)
from tests.helper_scripts.run_and_validate_request import run_and_validate_request
from tests.helper_scripts.simple_result_validators import check_response_status


# This endpoint no longer works because of the other data source endpoint
# It is interpreted as another data source id
# But we have not yet decided whether to modify or remove it entirely
# def test_data_sources_map_get(
#     flask_client_with_db, connection_with_test_data: psycopg.Connection
# ):
#     """
#     Test that GET call to /data-sources-map endpoint retrieves data sources and verifies the location (latitude and longitude) of a specific source by name
#     """
#     tus = create_test_user_setup(flask_client_with_db)
#     response_json = run_and_validate_request(
#         flask_client=flask_client_with_db,
#         http_method="get",
#         endpoint="/api/data-sources/data-sources-map",
#         headers=tus.api_authorization_header,
#     )
#     data = response_json["data"]
#     found_source = False
#     for result in data:
#         name = result["name"]
#         if name != "Source 1":
#             continue
#         found_source = True
#         assert result["lat"] == 30
#         assert result["lng"] == 20
#     assert found_source
