from marshmallow import fields

from middleware.schema_and_dto_logic.schemas.data_requests.base import (
    DataRequestsSchema,
)
from middleware.schema_and_dto_logic.schemas.locations.info.response import (
    LocationInfoResponseSchema,
)
from middleware.schema_and_dto_logic.schemas.data_sources.expanded import (
    DataSourceExpandedSchema,
)
from middleware.schema_and_dto_logic.util import (
    get_json_metadata,
)


class DataRequestsGetSchemaBase(DataRequestsSchema):
    data_sources = fields.List(
        fields.Nested(
            nested=DataSourceExpandedSchema(only=["id", "name"]),
            metadata=get_json_metadata(
                "The data sources associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The data sources associated with the data request"),
    )
    data_source_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The data source ids associated with the data request."
            ),
        ),
        metadata=get_json_metadata(
            "The data source ids associated with the data request."
        ),
    )
    locations = fields.List(
        fields.Nested(
            nested=LocationInfoResponseSchema(),
            metadata=get_json_metadata(
                "The locations associated with the data request"
            ),
        ),
        required=True,
        metadata=get_json_metadata("The locations associated with the data request"),
    )
    location_ids = fields.List(
        fields.Integer(
            allow_none=True,
            metadata=get_json_metadata(
                "The location ids associated with the data request."
            ),
        ),
        metadata=get_json_metadata(
            "The location ids associated with the data request."
        ),
    )
