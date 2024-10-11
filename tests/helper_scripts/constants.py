import urllib.parse
from collections import namedtuple
from http import HTTPStatus

from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO

DATA_SOURCES_BASE_ENDPOINT = "/api/data-sources"
DATA_SOURCES_BY_ID_ENDPOINT = DATA_SOURCES_BASE_ENDPOINT + "/{data_source_id}"

DATA_REQUESTS_BASE_ENDPOINT = "/api/data-requests"
DATA_REQUESTS_BY_ID_ENDPOINT = DATA_REQUESTS_BASE_ENDPOINT + "/"
DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT = (
    DATA_REQUESTS_BY_ID_ENDPOINT + "{data_request_id}/related-sources"
)
DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT = (
    DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT + "/{source_id}"
)

AGENCIES_BASE_ENDPOINT = "/api/agencies"
AGENCIES_BY_ID_ENDPOINT = AGENCIES_BASE_ENDPOINT + "/{agency_id}"

GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT = "/api/github/data-requests/issues/{data_request_id}"
GITHUB_DATA_REQUESTS_SYNCHRONIZE = "/api/github/data-requests/synchronize"


GET_MANY_TEST_QUERY_ARGS = "query_dict,expected_dto"
GET_MANY_TEST_QUERY_PARAMS = (
    ({"page": "1"}, GetManyBaseDTO(page=1, sort_order=SortOrder.DESCENDING)),
    (
        {"page": "1", "sort_by": "column1"},
        GetManyBaseDTO(page=1, sort_by="column1", sort_order=SortOrder.DESCENDING),
    ),
    (
        {"page": "1", "sort_by": "column1", "sort_order": "DESC"},
        GetManyBaseDTO(page=1, sort_by="column1", sort_order=SortOrder.DESCENDING),
    ),
    (
        {"page": "1", "sort_by": "column1", "sort_order": "ASC"},
        GetManyBaseDTO(page=1, sort_by="column1", sort_order=SortOrder.ASCENDING),
    ),
    (
        {"page": "1", "requested_columns": str(["columnA", "columnB"])},
        GetManyBaseDTO(
            page=1,
            requested_columns=["columnA", "columnB"],
            sort_order=SortOrder.DESCENDING,
        ),
    ),
)
ResponseTuple = namedtuple("ResponseTuple", ["response", "status_code"])
TEST_RESPONSE = ResponseTuple(
    response={"message": "Test Response"}, status_code=HTTPStatus.IM_A_TEAPOT
)
