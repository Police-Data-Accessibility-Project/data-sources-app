from marshmallow import fields

from endpoints.instantiations.agencies_.get._shared.dto.base import AgenciesGetDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.agencies.base import AgencyInfoBaseSchema
from middleware.schema_and_dto.schemas.agencies.helpers import (
    get_name_field,
    get_jurisdiction_type_field,
)
from endpoints.instantiations.data_sources_._shared.schemas.expanded import (
    DataSourceExpandedSchema,
)
from endpoints.instantiations.locations_._shared.schemas.response import (
    LocationInfoResponseSchema,
)
from middleware.schema_and_dto.schemas.locations._helpers import (
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    LOCALITY_NAME_FIELD,
)
from middleware.schema_and_dto.util import get_json_metadata
from utilities.enums import SourceMappingEnum


AgenciesGetSchema = pydantic_to_marshmallow(AgenciesGetDTO)
