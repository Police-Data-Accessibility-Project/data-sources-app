from marshmallow import Schema

from endpoints.instantiations.agencies_.put.dto import AgencyInfoPutDTO
from middleware.schema_and_dto.schemas.agencies.helpers import (
    get_agency_info_field,
)
from endpoints.instantiations.agencies_.put.schemas.inner import (
    AgencyInfoPutSchema,
)


class AgenciesPutSchema(Schema):
    #
    agency_info = get_agency_info_field(
        schema=AgencyInfoPutSchema,
        nested_dto_class=AgencyInfoPutDTO,
    )
