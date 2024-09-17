from database_client.enums import SortOrder
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO

DATA_SOURCES_BASE_ENDPOINT = "/api/data-sources"
DATA_SOURCES_BY_ID_ENDPOINT = DATA_SOURCES_BASE_ENDPOINT + "/{data_source_id}"

DATA_REQUESTS_BASE_ENDPOINT = "/api/data-requests"
DATA_REQUESTS_BY_ID_ENDPOINT = DATA_REQUESTS_BASE_ENDPOINT + "/"
DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT = DATA_REQUESTS_BY_ID_ENDPOINT + "{data_request_id}/related-sources"
DATA_REQUESTS_POST_DELETE_RELATED_SOURCE_ENDPOINT = DATA_REQUESTS_GET_RELATED_SOURCE_ENDPOINT + "/{source_id}"

AGENCIES_BASE_ENDPOINT = "/api/agencies"
AGENCIES_BY_ID_ENDPOINT = AGENCIES_BASE_ENDPOINT + "/{agency_id}"


GET_MANY_TEST_QUERY_PARAMS = (
        ({"page": "1"}, GetManyBaseDTO(page=1, sort_order=SortOrder.DESCENDING)),
        (
            {"page": "1", "sort_by": "agency_name"},
            GetManyBaseDTO(page=1, sort_by="agency_name", sort_order=SortOrder.DESCENDING),
        ),
        (
            {"page": "1", "sort_by": "agency_name", "sort_order": "DESC"},
            GetManyBaseDTO(
                page=1, sort_by="agency_name", sort_order=SortOrder.DESCENDING
            ),
        ),
        (
            {"page": "1", "sort_by": "agency_name", "sort_order": "ASC"},
            GetManyBaseDTO(
                page=1, sort_by="agency_name", sort_order=SortOrder.ASCENDING
            ),
        ),
        (
            {"page": "1", "requested_columns": "column1,column2"},
            GetManyBaseDTO(page=1, requested_columns=["column1", "column2"], sort_order=SortOrder.DESCENDING),
        ),
)