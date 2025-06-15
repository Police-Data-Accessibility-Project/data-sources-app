from typing import Optional

from db.enums import ApprovalStatus
from middleware.schema_and_dto.dtos.common.base import GetManyBaseDTO


class AgenciesGetManyDTO(GetManyBaseDTO):
    approval_status: Optional[ApprovalStatus] = None
