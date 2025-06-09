from marshmallow import Schema, fields

from middleware.enums import OutputFormatEnum
from middleware.schema_and_dto.schemas.search._helpers import (
    RECORD_CATEGORY_METADATA,
    RECORD_TYPE_METADATA,
)
from middleware.schema_and_dto.util import get_query_metadata
from utilities.enums import SourceMappingEnum, ParserLocation


class SearchRequestSchema(Schema):
    location_id = fields.Int(
        required=False,
        metadata=get_query_metadata("The location ID of the search."),
    )
    record_categories = fields.Str(
        required=False,
        load_default="All",
        metadata=RECORD_CATEGORY_METADATA,
    )
    record_types = fields.Str(
        required=False,
        metadata=RECORD_TYPE_METADATA,
    )

    output_format = fields.Enum(
        required=False,
        enum=OutputFormatEnum,
        by_value=fields.Str,
        load_default=OutputFormatEnum.JSON.value,
        metadata={
            "description": "The output format of the search.",
            "source": SourceMappingEnum.QUERY_ARGS,
            "location": ParserLocation.QUERY.value,
        },
    )
