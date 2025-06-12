from flask import Response, make_response

from db.client import DatabaseClient
from middleware.security.access_info.primary import AccessInfoPrimary
from middleware.primary_resource_logic.search.helpers import (
    get_explicit_record_categories,
)
from middleware.schema_and_dto.dtos.search.federal import FederalSearchRequestDTO


def federal_search_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: FederalSearchRequestDTO,
) -> Response:
    explicit_record_categories = get_explicit_record_categories(dto.record_categories)
    search_results = db_client.search_federal_records(
        record_categories=explicit_record_categories,
        page=dto.page,
    )
    return make_response(
        {
            "results": search_results,
            "count": len(search_results),
        }
    )
