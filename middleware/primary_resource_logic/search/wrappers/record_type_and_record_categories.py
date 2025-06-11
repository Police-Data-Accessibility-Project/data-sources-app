from flask import Response

from db.client import DatabaseClient
from middleware.access_logic import AccessInfoPrimary
from middleware.primary_resource_logic.search.helpers import (
    create_search_record,
    get_explicit_record_categories,
    send_search_results,
)
from middleware.schema_and_dto.dtos.search.request import SearchRequestsDTO


def search_wrapper(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestsDTO,
) -> Response:
    create_search_record(access_info, db_client, dto)
    explicit_record_categories = get_explicit_record_categories(dto.record_categories)
    search_results = db_client.search_with_location_and_record_type(
        location_id=dto.location_id,
        record_categories=explicit_record_categories,
        record_types=dto.record_types,
        # Pass modified record categories, which breaks down ALL into individual categories
    )
    return send_search_results(
        search_results=search_results,
        output_format=dto.output_format,
    )
