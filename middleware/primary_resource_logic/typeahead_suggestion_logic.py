from typing import Callable
from database_client.database_client import DatabaseClient
from middleware.schema_and_dto_logic.common_schemas_and_dtos import TypeaheadDTO, TypeaheadSchema

def get_typeahead_results(
    db_client: DatabaseClient,
    dto: TypeaheadDTO,
    db_client_method: Callable
):
    return {
        "suggestions": db_client_method(db_client, dto.query)
    }

