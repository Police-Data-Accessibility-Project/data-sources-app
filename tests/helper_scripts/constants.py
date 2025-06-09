import urllib.parse
from collections import namedtuple
from http import HTTPStatus

from db.enums import SortOrder
from middleware.schema_and_dto.dtos.common.base import GetManyBaseDTO

# region Users

USERS_BASE_ENDPOINT = "/api/user"

# endregion

DATA_SOURCES_BASE_ENDPOINT = "/api/data-sources"
DATA_SOURCES_BY_ID_ENDPOINT = DATA_SOURCES_BASE_ENDPOINT + "/{data_source_id}"
DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT = (
    DATA_SOURCES_BY_ID_ENDPOINT + "/related-agencies"
)
DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT = (
    DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT + "/{agency_id}"
)

# region Data Requests
DATA_REQUESTS_BASE_ENDPOINT = "/api/data-requests"
DATA_REQUESTS_BY_ID_ENDPOINT = DATA_REQUESTS_BASE_ENDPOINT + "/{data_request_id}"
DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT = (
    DATA_REQUESTS_BY_ID_ENDPOINT + "/related-sources"
)
DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT = (
    DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT + "/{source_id}"
)

DATA_REQUESTS_RELATED_LOCATIONS = DATA_REQUESTS_BY_ID_ENDPOINT + "/related-locations"
DATA_REQUESTS_POST_DELETE_RELATED_LOCATIONS_ENDPOINT = (
    DATA_REQUESTS_RELATED_LOCATIONS + "/{location_id}"
)
# endregion

NOTIFICATIONS_BASE_ENDPOINT = "/api/notifications"

USER_PROFILE_RECENT_SEARCHES_ENDPOINT = "/api/user/recent-searches"


AGENCIES_BASE_ENDPOINT = "/api/agencies"
AGENCIES_BY_ID_ENDPOINT = AGENCIES_BASE_ENDPOINT + "/{agency_id}"

GITHUB_DATA_REQUESTS_ISSUES_ENDPOINT = (
    "/api/github/data-requests/issues/{data_request_id}"
)
GITHUB_DATA_REQUESTS_SYNCHRONIZE = "/api/github/data-requests/synchronize"

# region Github OAuth
GITHUB_OAUTH_LINK_ENDPOINT = "/api/oauth/link-to-github"

GITHUB_OAUTH_LOGIN_ENDPOINT = "/api/oauth/login-with-github"

# endregion

SEARCH_FOLLOW_BASE_ENDPOINT = "/api/search/follow"


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
