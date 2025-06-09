from typing import Optional

from db.enums import RequestStatus
from middleware.schema_and_dto_logic.dtos.common.base import GetManyBaseDTO


class GetManyDataRequestsRequestsDTO(GetManyBaseDTO):
    request_statuses: Optional[list[RequestStatus]] = None
