from marshmallow import Schema, fields

from middleware.schema_and_dto.schemas.search._helpers import (
    RECORD_CATEGORY_METADATA,
)
from middleware.schema_and_dto.util import get_query_metadata


class FederalSearchRequestSchema(Schema):
    record_categories = fields.Str(
        required=False,
        load_default="All",
        metadata=RECORD_CATEGORY_METADATA,
    )
    page = fields.Int(
        required=False,
        load_default=1,
        metadata=get_query_metadata(
            "The page number of the results to retrieve. Begins at 1."
        ),
    )
