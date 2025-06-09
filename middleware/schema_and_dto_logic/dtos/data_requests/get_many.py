from typing import Optional

from db.enums import RequestStatus
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


class GetManyDataRequestsRequestsDTO(GetManyBaseDTO):
    request_statuses: Optional[list[RequestStatus]] = None
