from marshmallow import fields

from middleware.enums import RecordTypes
from endpoints.instantiations.data_sources_._shared.schemas.base import (
    DataSourceBaseSchema,
)
from middleware.schema_and_dto.util import get_json_metadata


class DataSourceExpandedSchema(DataSourceBaseSchema):
    record_type_name = fields.Enum(
        enum=RecordTypes,
        by_value=fields.Str,
        allow_none=True,
        metadata=get_json_metadata(
            "The record type of the data source.",
        ),
    )
