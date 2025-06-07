from marshmallow import Schema

from middleware.schema_and_dto_logic.dtos.agencies_dtos import AgencyInfoPutDTO
from middleware.schema_and_dto_logic.schemas.agencies.helpers import (
    get_agency_info_field,
)
from middleware.schema_and_dto_logic.schemas.agencies.info.put import (
    AgencyInfoPutSchema,
)


class AgenciesPutSchema(Schema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        nested_dto_class=AgencyInfoPutDTO,
    )
