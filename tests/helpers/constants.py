from collections import namedtuple
from http import HTTPStatus


DATA_SOURCES_BASE_ENDPOINT = "/data-sources"
DATA_SOURCES_BY_ID_ENDPOINT = DATA_SOURCES_BASE_ENDPOINT + "/{data_source_id}"
DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT = (
    DATA_SOURCES_BY_ID_ENDPOINT + "/related-agencies"
)
DATA_SOURCES_POST_DELETE_RELATED_AGENCY_ENDPOINT = (
    DATA_SOURCES_GET_RELATED_AGENCIES_ENDPOINT + "/{agency_id}"
)

# region Data Requests
DATA_REQUESTS_BASE_ENDPOINT = "/data-requests"
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

NOTIFICATIONS_BASE_ENDPOINT = "/notifications"

USER_PROFILE_RECENT_SEARCHES_ENDPOINT = "/user/recent-searches"


AGENCIES_BASE_ENDPOINT = "/agencies"

# region Github OAuth
GITHUB_OAUTH_LINK_ENDPOINT = "/oauth/link-to-github"

GITHUB_OAUTH_LOGIN_ENDPOINT = "/oauth/login-with-github"

# endregion

SEARCH_FOLLOW_BASE_ENDPOINT = "/search/follow"

ResponseTuple = namedtuple("ResponseTuple", ["response", "status_code"])
TEST_RESPONSE = ResponseTuple(
    response={"message": "Test Response"}, status_code=HTTPStatus.IM_A_TEAPOT
)
