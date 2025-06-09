from marshmallow import Schema, fields

from middleware.schema_and_dto.schemas.locations.map.counties import (
    CountiesLocationsMapInnerSchema,
)
from middleware.schema_and_dto.schemas.locations.map.localities import (
    LocalitiesLocationsMapInnerSchema,
)
from middleware.schema_and_dto.schemas.locations.map.states import (
    StatesLocationsMapInnerSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class LocationsMapResponseSchema(Schema):
    localities = fields.List(
        fields.Nested(
            LocalitiesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of localities"),
        ),
        required=True,
        metadata=get_json_metadata("The list of localities"),
    )
    counties = fields.List(
        fields.Nested(
            CountiesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of counties"),
        ),
        required=True,
        metadata=get_json_metadata("The list of counties"),
    )
    states = fields.List(
        fields.Nested(
            StatesLocationsMapInnerSchema(),
            required=True,
            metadata=get_json_metadata("The list of states"),
        ),
        required=True,
        metadata=get_json_metadata("The list of states"),
    )
