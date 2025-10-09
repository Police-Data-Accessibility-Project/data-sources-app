from endpoints.instantiations.search.core.models.response import SearchResponseDTO
from endpoints.instantiations.search.core.schemas.response import SearchResponseSchema
from middleware.enums import RecordTypes
from tests.helpers.helper_classes.RequestValidator import RequestValidator
from tests.helpers.helper_functions_simple import add_query_params
from utilities.enums import RecordCategoryEnum


def request_validator_search(
    request_validator: RequestValidator,
    headers: dict,
    location_id: int | None = None,
    record_types: list[RecordTypes] | None = None,
    record_categories: list[RecordCategoryEnum] | None = None,
) -> SearchResponseDTO:
    endpoint_base: str = "/search"
    query_params: dict[str, str] = request_validator._get_search_query_params(
        location_id=location_id,
        record_types=record_types,
        record_categories=record_categories,
    )
    endpoint: str = add_query_params(
        url=endpoint_base,
        params=query_params,
    )

    json: dict = request_validator.get(
        endpoint=endpoint,
        headers=headers,
        expected_schema=SearchResponseSchema,
        location_id=location_id,
        record_types=record_types,
        record_categories=record_categories,
    )
    return SearchResponseDTO(**json)