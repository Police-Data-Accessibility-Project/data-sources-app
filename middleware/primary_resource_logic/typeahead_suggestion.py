from typing import Callable

from db.client import DatabaseClient
from middleware.flask_response_manager import FlaskResponseManager
from middleware.schema_and_dto_logic.dtos.typeahead import TypeaheadDTO
from utilities.enums import SourceMappingEnum

RESPONSE_METADATA = {
    "source": SourceMappingEnum.JSON,
}


def get_typeahead_results(
    db_client: DatabaseClient,
    dto: TypeaheadDTO,
    db_client_method: Callable,
):
    return FlaskResponseManager.make_response(
        data={"suggestions": db_client_method(db_client, dto.query)},
    )
