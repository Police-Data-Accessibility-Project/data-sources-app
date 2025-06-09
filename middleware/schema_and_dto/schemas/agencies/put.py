from marshmallow import Schema

from middleware.schema_and_dto.dtos.agencies.put import AgencyInfoPutDTO
from middleware.schema_and_dto.schemas.agencies.helpers import (
    get_agency_info_field,
)
from middleware.schema_and_dto.schemas.agencies.info.put import (
    AgencyInfoPutSchema,
)


class AgenciesPutSchema(Schema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        nested_dto_class=AgencyInfoPutDTO,
    )
