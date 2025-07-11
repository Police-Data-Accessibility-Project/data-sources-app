from marshmallow import fields

from endpoints.instantiations.data_requests_._shared.dtos.get import DataRequestsGetDTOBase
from endpoints.instantiations.data_requests_._shared.schemas.base import DataRequestsSchema
from endpoints.instantiations.data_sources_._shared.schemas.expanded import DataSourceExpandedSchema
from endpoints.instantiations.locations_._shared.schemas.response import LocationInfoResponseSchema
from middleware.schema_and_dto.dynamic.pydantic_to_marshmallow.core import pydantic_to_marshmallow
from middleware.schema_and_dto.util import get_json_metadata


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

# DataRequestsGetSchemaBase = pydantic_to_marshmallow(DataRequestsGetDTOBase)