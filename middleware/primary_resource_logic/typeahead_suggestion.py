from typing import Callable

from flask import make_response

from db.client.core import DatabaseClient
from middleware.schema_and_dto.dtos.typeahead import TypeaheadDTO
from utilities.enums import SourceMappingEnum

RESPONSE_METADATA = {
    "source": SourceMappingEnum.JSON,
}


def get_typeahead_results(
    db_client: DatabaseClient,
    dto: TypeaheadDTO,
    db_client_method: Callable,
):
    return make_response(
        {"suggestions": db_client_method(db_client, dto.query, dto.page)}
    )
