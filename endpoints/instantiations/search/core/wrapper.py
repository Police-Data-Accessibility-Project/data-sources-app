from flask import Response

from db.client.core import DatabaseClient
from db.queries.instantiations.search.record import CreateSearchRecordQueryBuilder
from endpoints.instantiations.search.core.models.request import SearchRequestDTO
from endpoints.instantiations.search.core.models.response import SearchResponseDTO
from endpoints.instantiations.search.core.queries.core import SearchQueryBuilder
from middleware.primary_resource_logic.search.helpers import (
    create_search_record,
    get_explicit_record_categories,
)
from middleware.security.access_info.primary import AccessInfoPrimary
from utilities.enums import RecordCategoryEnum


def _create_search_record(
    access_info: AccessInfoPrimary, db_client: DatabaseClient, dto: SearchRequestDTO
):
    builder = CreateSearchRecordQueryBuilder(
        user_id=access_info.user_id,
        location_id=dto.location_id,
        record_categories=dto.record_categories,
        record_types=dto.record_types,
    )
    return db_client.run_query_builder(builder)


def search_wrapper_v2(
    db_client: DatabaseClient,
    access_info: AccessInfoPrimary,
    dto: SearchRequestDTO,
) -> Response:
    create_search_record(access_info, db_client=db_client, dto=dto)
    explicit_record_categories: list[RecordCategoryEnum] | None = (
        get_explicit_record_categories(dto.record_categories)
    )
    search_results: SearchResponseDTO = db_client.run_query_builder(
        SearchQueryBuilder(
            location_id=dto.location_id,
            record_categories=explicit_record_categories,
            record_types=dto.record_types,
        )
    )
    return search_results.model_dump(mode="json")
