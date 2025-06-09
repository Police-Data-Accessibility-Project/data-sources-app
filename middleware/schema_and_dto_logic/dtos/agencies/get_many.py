from typing import Optional

from db.enums import ApprovalStatus
from middleware.schema_and_dto_logic.common_schemas_and_dtos import GetManyBaseDTO


class AgenciesGetManyDTO(GetManyBaseDTO):
    approval_status: Optional[ApprovalStatus] = None
