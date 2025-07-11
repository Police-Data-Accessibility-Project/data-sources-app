from marshmallow import Schema

from endpoints.instantiations.locations_._shared.dtos.response import LocationInfoResponseDTO
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.schemas.locations._helpers import (
    LOCATION_TYPE_FIELD,
    STATE_NAME_FIELD,
    STATE_ISO_FIELD,
    COUNTY_FIPS_FIELD,
    COUNTY_NAME_FIELD,
    LOCALITY_NAME_FIELD,
    DISPLAY_NAME_FIELD,
    LOCATION_ID_FIELD,
)

LocationInfoResponseSchema = pydantic_to_marshmallow(LocationInfoResponseDTO)